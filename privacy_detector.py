#!/usr/bin/env python3
"""
个人隐私信息检测程序
使用 OpenAI Vision API 分析图片中是否包含敏感个人信息
"""

import os
import base64
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import argparse

try:
    from openai import OpenAI
except ImportError:
    print("请先安装 openai 库: pip install openai")
    exit(1)

# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

class PrivacyDetector:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        """
        初始化隐私检测器

        Args:
            api_key: OpenAI API Key
            base_url: API Base URL (可选，用于自定义端点)
            model: 使用的模型，默认 gpt-4o
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model

    def encode_image(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self, image_path: str) -> Dict:
        """
        分析单张图片是否包含隐私信息

        Returns:
            包含分析结果的字典
        """
        try:
            # 读取并编码图片
            base64_image = self.encode_image(image_path)
            file_ext = Path(image_path).suffix.lower()

            # 确定 MIME 类型
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(file_ext, 'image/png')

            # 调用 OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """请仔细分析这张图片，识别是否包含以下类型的个人隐私信息：

1. 身份证信息（身份证号、证件照片）
2. 手机号码
3. 电子邮箱地址
4. 家庭住址或详细地理位置
5. 银行卡号或支付信息
6. 个人照片（清晰的人脸）
7. 真实姓名配合其他敏感信息
8. 密码或密钥信息
9. 其他可识别个人身份的敏感信息

请以 JSON 格式回复，包含以下字段：
{
  "has_privacy": true/false,
  "risk_level": "high/medium/low/none",
  "privacy_types": ["类型1", "类型2"],
  "description": "详细说明发现的隐私信息",
  "suggestion": "处理建议"
}

如果图片只是代码、设计文档、技术图表等工作内容，请标记为无隐私风险。"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            # 解析响应
            content = response.content[0].text if hasattr(response, 'content') else response.choices[0].message.content

            # 尝试解析 JSON
            try:
                # 查找 JSON 内容
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0].strip()
                else:
                    json_str = content.strip()

                result = json.loads(json_str)
            except json.JSONDecodeError:
                # 如果无法解析 JSON，返回原始内容
                result = {
                    "has_privacy": False,
                    "risk_level": "unknown",
                    "privacy_types": [],
                    "description": content,
                    "suggestion": "无法解析 AI 响应"
                }

            return {
                "success": True,
                "image_path": image_path,
                "result": result
            }

        except Exception as e:
            return {
                "success": False,
                "image_path": image_path,
                "error": str(e)
            }

    def scan_directory(self, directory: str, output_file: str = None) -> Dict:
        """
        扫描目录下的所有图片

        Args:
            directory: 要扫描的目录
            output_file: 输出报告文件路径（可选）

        Returns:
            扫描结果汇总
        """
        directory_path = Path(directory)

        # 查找所有支持的图片文件
        image_files = []
        for ext in SUPPORTED_FORMATS:
            image_files.extend(directory_path.glob(f"*{ext}"))

        print(f"找到 {len(image_files)} 张图片，开始分析...")

        results = {
            "scan_time": datetime.now().isoformat(),
            "total_images": len(image_files),
            "analyzed": 0,
            "failed": 0,
            "privacy_found": 0,
            "high_risk": [],
            "medium_risk": [],
            "low_risk": [],
            "no_risk": [],
            "failed_images": []
        }

        # 分析每张图片
        for idx, image_file in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] 分析: {image_file.name}")

            analysis = self.analyze_image(str(image_file))

            if analysis["success"]:
                results["analyzed"] += 1
                result = analysis["result"]

                if result.get("has_privacy", False):
                    results["privacy_found"] += 1

                risk_level = result.get("risk_level", "unknown")
                image_info = {
                    "file": image_file.name,
                    "path": str(image_file),
                    "risk_level": risk_level,
                    "privacy_types": result.get("privacy_types", []),
                    "description": result.get("description", ""),
                    "suggestion": result.get("suggestion", "")
                }

                if risk_level == "high":
                    results["high_risk"].append(image_info)
                elif risk_level == "medium":
                    results["medium_risk"].append(image_info)
                elif risk_level == "low":
                    results["low_risk"].append(image_info)
                else:
                    results["no_risk"].append(image_info)
            else:
                results["failed"] += 1
                results["failed_images"].append({
                    "file": image_file.name,
                    "error": analysis["error"]
                })
                print(f"  ⚠️  分析失败: {analysis['error']}")

        # 生成报告
        self._print_summary(results)

        # 保存报告到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n详细报告已保存到: {output_file}")

        return results

    def _print_summary(self, results: Dict):
        """打印扫描结果摘要"""
        print("\n" + "="*60)
        print("扫描结果汇总")
        print("="*60)
        print(f"扫描时间: {results['scan_time']}")
        print(f"总图片数: {results['total_images']}")
        print(f"分析成功: {results['analyzed']}")
        print(f"分析失败: {results['failed']}")
        print(f"发现隐私: {results['privacy_found']}")
        print()

        print(f"🔴 高风险图片: {len(results['high_risk'])} 张")
        for img in results['high_risk']:
            print(f"  - {img['file']}")
            print(f"    类型: {', '.join(img['privacy_types'])}")
            print(f"    说明: {img['description'][:100]}...")

        print(f"\n🟡 中风险图片: {len(results['medium_risk'])} 张")
        for img in results['medium_risk'][:5]:  # 只显示前5个
            print(f"  - {img['file']}")
            print(f"    类型: {', '.join(img['privacy_types'])}")

        if len(results['medium_risk']) > 5:
            print(f"  ... 还有 {len(results['medium_risk']) - 5} 张")

        print(f"\n🟢 低风险图片: {len(results['low_risk'])} 张")
        print(f"⚪ 无风险图片: {len(results['no_risk'])} 张")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description='个人隐私信息检测程序')
    parser.add_argument('--dir', '-d', default='img', help='要扫描的图片目录 (默认: img)')
    parser.add_argument('--output', '-o', default='privacy_report.json', help='输出报告文件路径')
    parser.add_argument('--api-key', '-k', help='OpenAI API Key (也可通过环境变量 OPENAI_API_KEY 设置)')
    parser.add_argument('--base-url', '-b', help='API Base URL (也可通过环境变量 OPENAI_BASE_URL 设置)')
    parser.add_argument('--model', '-m', default='gpt-4o', help='使用的模型 (默认: gpt-4o)')

    args = parser.parse_args()

    # 获取 API Key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("错误: 未提供 OpenAI API Key")
        print("请通过 --api-key 参数或设置 OPENAI_API_KEY 环境变量")
        exit(1)

    # 获取 Base URL（优先使用命令行参数，其次使用环境变量）
    base_url = args.base_url or os.getenv('OPENAI_BASE_URL')

    # 检查目录是否存在
    if not os.path.isdir(args.dir):
        print(f"错误: 目录不存在: {args.dir}")
        exit(1)

    # 创建检测器
    detector = PrivacyDetector(
        api_key=api_key,
        base_url=base_url,
        model=args.model
    )

    # 扫描目录
    try:
        detector.scan_directory(args.dir, args.output)
    except KeyboardInterrupt:
        print("\n\n扫描已中断")
    except Exception as e:
        print(f"\n错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
