# Windows 代理开关桌面应用

这是一个适用于 Windows 的轻量桌面工具（Python + Tkinter），用于：

- 一键开启/关闭系统代理
- 可选配置代理 IP 与端口
- 当 IP 与端口都留空时，开启代理只会打开 `ProxyEnable`，沿用系统当前代理地址

## 运行环境

- Windows 10/11
- Python 3.10+

## 运行方式

```bash
python proxy_switcher.py
```

## 打包成 exe（可选）

使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name ProxySwitcher proxy_switcher.py
```

输出文件位于：

- `dist/ProxySwitcher.exe`

## 说明

- 本程序修改的是当前用户的系统代理配置（注册表路径）：
  - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings`
- 若你在公司环境中受到组策略限制，可能无法修改代理设置。
