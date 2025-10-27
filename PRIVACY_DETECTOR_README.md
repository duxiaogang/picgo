# 个人隐私信息检测程序

这是一个使用 OpenAI Vision API 分析图片中是否包含个人隐私信息的工具。

## 功能特点

- 自动扫描指定目录下的所有图片
- 使用 AI 视觉识别技术分析图片内容
- 识别多种类型的隐私信息：
  - 身份证信息
  - 手机号码
  - 电子邮箱
  - 家庭住址
  - 银行卡号
  - 个人照片（人脸）
  - 真实姓名
  - 密码或密钥
- 按风险级别分类（高/中/低/无）
- 生成详细的 JSON 格式报告

## 安装依赖

```bash
pip install openai
```

## 使用方法

### 1. 设置 API Key

有两种方式设置 OpenAI API Key：

**方式一：环境变量**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**方式二：命令行参数**
```bash
python privacy_detector.py --api-key "your-api-key-here"
```

### 2. 设置自定义 API 端点（可选）

如果你使用的是 OpenAI 兼容的 API（如 Azure OpenAI、代理服务等），可以设置 Base URL：

**方式一：环境变量**
```bash
export OPENAI_BASE_URL="https://your-api-endpoint.com/v1"
```

**方式二：命令行参数**
```bash
python privacy_detector.py --base-url "https://your-api-endpoint.com/v1"
```

**注意**：如果使用 OpenAI 官方 API，无需设置此项。

### 3. 运行检测

**基本用法（扫描 img 目录）：**
```bash
python privacy_detector.py
```

**指定目录：**
```bash
python privacy_detector.py --dir /path/to/images
```

**完整参数示例：**
```bash
python privacy_detector.py \
  --dir img \
  --output privacy_report.json \
  --api-key "your-api-key" \
  --model gpt-4o
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--dir` | `-d` | 要扫描的图片目录 | `img` |
| `--output` | `-o` | 输出报告文件路径 | `privacy_report.json` |
| `--api-key` | `-k` | OpenAI API Key | 从环境变量 OPENAI_API_KEY 读取 |
| `--base-url` | `-b` | API Base URL（可选） | 从环境变量 OPENAI_BASE_URL 读取，默认使用 OpenAI 官方地址 |
| `--model` | `-m` | 使用的模型 | `gpt-4o` |

## 输出说明

### 控制台输出

程序会在控制台显示：
- 扫描进度
- 结果摘要
- 高风险和中风险图片列表

示例：
```
找到 453 张图片，开始分析...
[1/453] 分析: 1.png
[2/453] 分析: 20220429180429.png
...

============================================================
扫描结果汇总
============================================================
扫描时间: 2025-10-27T11:30:00
总图片数: 453
分析成功: 453
分析失败: 0
发现隐私: 5

🔴 高风险图片: 2 张
  - personal_id.png
    类型: 身份证信息, 真实姓名
    说明: 图片中包含身份证照片...

🟡 中风险图片: 3 张
  - screenshot1.png
    类型: 手机号码

🟢 低风险图片: 10 张
⚪ 无风险图片: 438 张
============================================================
```

### JSON 报告

程序会生成一个详细的 JSON 报告文件（默认为 `privacy_report.json`），包含：

```json
{
  "scan_time": "2025-10-27T11:30:00",
  "total_images": 453,
  "analyzed": 453,
  "failed": 0,
  "privacy_found": 5,
  "high_risk": [
    {
      "file": "personal_id.png",
      "path": "/Users/xxx/img/personal_id.png",
      "risk_level": "high",
      "privacy_types": ["身份证信息", "真实姓名"],
      "description": "图片中包含身份证照片...",
      "suggestion": "建议立即删除或加密存储"
    }
  ],
  "medium_risk": [...],
  "low_risk": [...],
  "no_risk": [...],
  "failed_images": [...]
}
```

## 风险级别说明

- **高风险（High）**：包含可直接识别个人身份的敏感信息，如身份证、银行卡等
- **中风险（Medium）**：包含部分个人信息，如单独的手机号、邮箱等
- **低风险（Low）**：包含轻微的个人信息，风险较小
- **无风险（None）**：纯工作内容，无个人隐私信息

## 注意事项

1. **API 费用**：使用 OpenAI Vision API 会产生费用，453 张图片大约消耗 $5-10（取决于图片大小）
2. **网络要求**：需要能够访问 OpenAI API（或你指定的端点）
3. **图片格式**：支持 PNG, JPG, JPEG, GIF, WEBP 格式
4. **准确性**：AI 分析可能存在误判，建议人工复核高风险图片
5. **处理速度**：分析速度取决于网络和 API 响应速度，大约每张图片 2-5 秒

## 后续处理建议

对于检测出的高风险图片，建议：
1. 人工复核确认
2. 删除包含隐私信息的图片
3. 或对敏感信息进行打码处理
4. 将隐私图片移动到安全的加密存储位置

## 批量处理示例

如果图片很多，可以分批处理：

```bash
# 只处理前 50 张（需要修改脚本支持）
# 或者先测试几张看效果
python privacy_detector.py --dir img/test_sample
```

## 故障排除

**问题：`ModuleNotFoundError: No module named 'openai'`**
```bash
pip install openai
```

**问题：API 请求失败**
- 检查 API Key 是否正确
- 检查网络连接
- 检查是否设置了正确的 base-url

**问题：分析速度太慢**
- 考虑使用更快的模型（如 `gpt-4o-mini`）
- 或先处理一部分图片测试

## 许可证

本程序仅供个人使用，请遵守相关法律法规和 OpenAI 使用条款。
