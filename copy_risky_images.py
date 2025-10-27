#!/usr/bin/env python3
"""
从隐私检测报告中提取有风险的图片并拷贝到独立目录
"""

import json
import shutil
import os
from pathlib import Path
import argparse


def copy_risky_images(report_file: str, output_dir: str = "risky_images"):
    """
    从报告中提取有风险的图片并拷贝到独立目录

    Args:
        report_file: 隐私检测报告文件路径
        output_dir: 输出目录路径
    """
    # 读取报告
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 创建子目录
    high_dir = output_path / "high_risk"
    medium_dir = output_path / "medium_risk"
    low_dir = output_path / "low_risk"

    high_dir.mkdir(exist_ok=True)
    medium_dir.mkdir(exist_ok=True)
    low_dir.mkdir(exist_ok=True)

    # 统计信息
    stats = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "failed": 0
    }

    print("开始拷贝有风险的图片...")
    print("="*60)

    # 拷贝高风险图片
    if report.get("high_risk"):
        print(f"\n🔴 高风险图片: {len(report['high_risk'])} 张")
        for img in report["high_risk"]:
            src = Path(img["path"])
            dst = high_dir / img["file"]

            try:
                shutil.copy2(src, dst)
                print(f"  ✓ {img['file']}")
                print(f"    风险类型: {', '.join(img['privacy_types'])}")
                print(f"    说明: {img['description'][:80]}...")
                stats["high"] += 1
            except Exception as e:
                print(f"  ✗ {img['file']} - 拷贝失败: {e}")
                stats["failed"] += 1

    # 拷贝中风险图片
    if report.get("medium_risk"):
        print(f"\n🟡 中风险图片: {len(report['medium_risk'])} 张")
        for img in report["medium_risk"]:
            src = Path(img["path"])
            dst = medium_dir / img["file"]

            try:
                shutil.copy2(src, dst)
                print(f"  ✓ {img['file']}")
                print(f"    风险类型: {', '.join(img['privacy_types'])}")
                stats["medium"] += 1
            except Exception as e:
                print(f"  ✗ {img['file']} - 拷贝失败: {e}")
                stats["failed"] += 1

    # 拷贝低风险图片
    if report.get("low_risk"):
        print(f"\n🟢 低风险图片: {len(report['low_risk'])} 张")
        for img in report["low_risk"]:
            src = Path(img["path"])
            dst = low_dir / img["file"]

            try:
                shutil.copy2(src, dst)
                print(f"  ✓ {img['file']}")
                stats["low"] += 1
            except Exception as e:
                print(f"  ✗ {img['file']} - 拷贝失败: {e}")
                stats["failed"] += 1

    # 如果某个风险级别没有图片，删除空目录
    if stats["high"] == 0:
        high_dir.rmdir()
    if stats["medium"] == 0:
        medium_dir.rmdir()
    if stats["low"] == 0:
        low_dir.rmdir()

    # 输出摘要
    print("\n" + "="*60)
    print("拷贝完成!")
    print("="*60)
    print(f"输出目录: {output_path.absolute()}")
    print(f"高风险图片: {stats['high']} 张 -> {high_dir.name}/" if stats['high'] > 0 else "高风险图片: 0 张")
    print(f"中风险图片: {stats['medium']} 张 -> {medium_dir.name}/" if stats['medium'] > 0 else "中风险图片: 0 张")
    print(f"低风险图片: {stats['low']} 张 -> {low_dir.name}/" if stats['low'] > 0 else "低风险图片: 0 张")

    if stats["failed"] > 0:
        print(f"\n⚠️  拷贝失败: {stats['failed']} 张")

    print("="*60)

    # 创建一个摘要文件
    summary_file = output_path / "summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"隐私风险图片拷贝摘要\n")
        f.write(f"{'='*60}\n")
        f.write(f"生成时间: {report.get('scan_time', 'Unknown')}\n")
        f.write(f"原始报告: {report_file}\n\n")

        f.write(f"高风险图片 ({stats['high']} 张):\n")
        f.write(f"{'-'*60}\n")
        for img in report.get("high_risk", []):
            f.write(f"文件: {img['file']}\n")
            f.write(f"风险类型: {', '.join(img['privacy_types'])}\n")
            f.write(f"说明: {img['description']}\n")
            f.write(f"建议: {img['suggestion']}\n")
            f.write(f"\n")

        f.write(f"\n中风险图片 ({stats['medium']} 张):\n")
        f.write(f"{'-'*60}\n")
        for img in report.get("medium_risk", []):
            f.write(f"文件: {img['file']}\n")
            f.write(f"风险类型: {', '.join(img['privacy_types'])}\n")
            f.write(f"说明: {img['description']}\n")
            f.write(f"建议: {img['suggestion']}\n")
            f.write(f"\n")

        if report.get("low_risk"):
            f.write(f"\n低风险图片 ({stats['low']} 张):\n")
            f.write(f"{'-'*60}\n")
            for img in report.get("low_risk", []):
                f.write(f"文件: {img['file']}\n")
                f.write(f"风险类型: {', '.join(img['privacy_types'])}\n")
                f.write(f"说明: {img['description']}\n")
                f.write(f"\n")

    print(f"\n详细摘要已保存到: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description='从隐私检测报告中提取有风险的图片')
    parser.add_argument('--report', '-r', default='privacy_report.json',
                        help='隐私检测报告文件路径 (默认: privacy_report.json)')
    parser.add_argument('--output', '-o', default='risky_images',
                        help='输出目录路径 (默认: risky_images)')

    args = parser.parse_args()

    if not os.path.exists(args.report):
        print(f"错误: 报告文件不存在: {args.report}")
        exit(1)

    copy_risky_images(args.report, args.output)


if __name__ == "__main__":
    main()
