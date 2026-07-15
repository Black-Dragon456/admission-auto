# admission-auto

高考录取结果自动查询脚本。项目目前保留两个版本分支：

- `v1`：浏览器自动化版本，使用 Playwright 打开查询页面、填写信息、识别验证码并点击查询。
- `v2`：无浏览器请求版本，使用 `requests` 直接提交查询表单，并解析页面中的成绩与录取信息。

> 注意：`config.ini` 会包含准考证号、身份证后四位等个人信息，请不要提交到公开仓库。

## 版本差异

| 版本 | 分支 | 查询方式 | 主要依赖 | 输出 |
| --- | --- | --- | --- | --- |
| v1 | `v1` | Playwright 浏览器自动化 | `playwright`、`ddddocr` | 控制台日志、`logs/result.log`、录取截图 |
| v2 | `v2` | `requests` 直接请求接口/页面 | `requests`、`lzstring`、`ddddocr` | 控制台日志、`logs/query.log`、`logs/result.log` |

### v1：浏览器自动化版

v1 会启动 Chromium，访问配置中的查询页面：

1. 填写准考证号和身份证后四位。
2. 从页面验证码图片中提取 base64 图片。
3. 使用 `ddddocr` 识别验证码。
4. 点击查询按钮。
5. 解析页面中激活的结果区域：
   - `#enresult1`：有录取信息。
   - `#enresult2`：暂无录取信息。
6. 查询到录取信息时保存结果区域截图。

适合页面结构经常变化、但浏览器手动查询仍可正常打开的情况。

### v2：无浏览器请求版

v2 不启动浏览器，查询流程为：

1. 创建 `requests.Session()` 并访问首页建立 Cookie。
2. 调用验证码接口获取验证码图片。
3. 使用 `ddddocr` 识别验证码。
4. 使用 `LZString.compressToBase64()` 兼容网页加密方式，压缩准考证号、身份证后四位和验证码。
5. 直接 POST 到查询地址。
6. 通过 `parser.py` 从返回 HTML 中提取 `_score` 和 `_luqu` 数据：
   - `_score`：成绩信息。
   - `_luqu`：录取信息。

适合服务器接口稳定、希望减少浏览器依赖和运行资源占用的情况。

## 环境要求

- Python 3.10 或更高版本
- Windows / macOS / Linux 均可运行
- v1 需要安装 Playwright 浏览器
- v2 不需要浏览器

## 安装依赖

建议先创建虚拟环境：

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

### 安装 v1 依赖

```bash
pip install playwright ddddocr
playwright install chromium
```

### 安装 v2 依赖

```bash
pip install requests lzstring ddddocr
```

## 配置文件

在项目根目录创建 `config.ini`：

```ini
[system]
url = https://你的查询地址
exam_no = 你的准考证号
id_card_last4 = 身份证后四位
headless = true
interval = 300
screenshot_dir = screenshots
logs_dir = logs
browser_path =
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `url` | 查询页面地址。v2 会直接向该地址提交 POST 请求 |
| `exam_no` | 准考证号 |
| `id_card_last4` | 身份证号后四位 |
| `headless` | 是否无头运行浏览器。主要用于 v1 |
| `interval` | 查询间隔，单位为秒 |
| `screenshot_dir` | 截图保存目录。主要用于 v1 |
| `logs_dir` | 日志保存目录 |
| `browser_path` | 自定义浏览器路径。为空时使用 Playwright 默认 Chromium，主要用于 v1 |

> v2 当前仍会读取 `headless`、`screenshot_dir`、`browser_path` 等字段，请在配置中保留这些字段，即使它们在 v2 流程中不直接使用。

## 运行

切换到对应版本分支：

```bash
git checkout v1
```

或：

```bash
git checkout v2
```

运行脚本：

```bash
python main.py
```

程序会按 `interval` 设置循环查询。按 `Ctrl+C` 可停止运行。

## 输出文件

### v1

- `logs/query.log`：主循环查询日志。
- `logs/result.log`：查询结果日志。
- `screenshots/*.png`：查询到录取信息后保存的结果区域截图。

### v2

- `logs/query.log`：每次验证码、查询状态和异常信息。
- `logs/result.log`：结构化查询结果，包含成绩和录取信息。

v2 查询成功时返回的数据结构大致如下：

```json
{
  "success": true,
  "admitted": true,
  "message": "已查询到录取信息",
  "admission": {
    "考生状态": "",
    "院校代号": "",
    "院校名称": "",
    "专业组名称": "",
    "专业代号": "",
    "专业名称": "",
    "批次名称": "",
    "科类名称": "",
    "计划性质": ""
  },
  "score": {
    "姓名": "",
    "准考证号": "",
    "考生号": "",
    "语文": "",
    "数学": "",
    "外语": "",
    "总分": "",
    "排名": ""
  }
}
```

## 打包为 exe

可使用 PyInstaller 打包：

```bash
pip install pyinstaller
pyinstaller -F main.py
```

打包完成后，把 `config.ini` 放在生成的 `main.exe` 同级目录。程序会在 exe 所在目录读取配置，并创建日志、截图目录。

v1 打包时请确保目标机器可以运行浏览器；如果使用系统 Chrome/Edge，可以在 `browser_path` 中填写浏览器可执行文件路径。

## 常见问题

### 提示 `config.ini` 不存在

确认 `config.ini` 与 `main.py` 在同一目录。打包后则需要与 `main.exe` 在同一目录。

### 验证码连续失败

可能原因：

- 验证码识别错误。
- 页面或验证码接口发生变化。
- 网络请求过慢或被限制。

可以降低查询频率，或临时打开 v1 的有头模式：

```ini
headless = false
```

### v1 页面元素找不到

说明查询页面结构可能变化了。重点检查以下选择器：

- `#key1`
- `#key2`
- `input.code`
- `#btncx`
- `.img-verifycode`
- `#enresult1`
- `#enresult2`

### v2 解析失败

v2 依赖返回页面中的 JS 变量：

- `_score`
- `_luqu`

如果网站调整了返回结构，需要同步修改 `parser.py`。

## 安全提醒

- 不要把真实 `config.ini` 上传到公开仓库。
- 不要高频请求查询网站，建议设置合理的 `interval`。
- 查询结果包含个人信息，日志和截图请妥善保存。
