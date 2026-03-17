import ctypes
import tkinter as tk
from tkinter import messagebox
import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37


def _refresh_system_proxy() -> None:
    """Notify Windows that Internet Settings changed."""
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)


def read_proxy_settings() -> tuple[bool, str]:
    """Return (proxy_enabled, proxy_server)."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
        enabled = bool(winreg.QueryValueEx(key, "ProxyEnable")[0])
        server = str(winreg.QueryValueEx(key, "ProxyServer")[0]) if _key_exists(key, "ProxyServer") else ""
    return enabled, server


def _key_exists(key: winreg.HKEYType, name: str) -> bool:
    try:
        winreg.QueryValueEx(key, name)
        return True
    except FileNotFoundError:
        return False


def set_proxy(enable: bool, server: str | None = None) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
        if server is not None:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, server)
    _refresh_system_proxy()


class ProxySwitcherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Windows 代理开关")
        self.root.resizable(False, False)

        self.status_var = tk.StringVar()

        container = tk.Frame(root, padx=16, pady=16)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="代理 IP：").grid(row=0, column=0, sticky="e", pady=4)
        tk.Label(container, text="端口：").grid(row=1, column=0, sticky="e", pady=4)

        self.ip_entry = tk.Entry(container, width=24)
        self.port_entry = tk.Entry(container, width=24)
        self.ip_entry.grid(row=0, column=1, pady=4)
        self.port_entry.grid(row=1, column=1, pady=4)

        tk.Label(
            container,
            text="留空 IP 与端口时，开启代理将沿用当前系统代理地址。",
            fg="#555",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 10))

        button_row = tk.Frame(container)
        button_row.grid(row=3, column=0, columnspan=2, pady=(0, 8))

        tk.Button(button_row, text="开启代理", width=12, command=self.enable_proxy).pack(side="left", padx=4)
        tk.Button(button_row, text="关闭代理", width=12, command=self.disable_proxy).pack(side="left", padx=4)
        tk.Button(button_row, text="刷新状态", width=12, command=self.refresh_status).pack(side="left", padx=4)

        tk.Label(container, textvariable=self.status_var, anchor="w", justify="left").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )

        self.load_existing_server()
        self.refresh_status()

    def load_existing_server(self) -> None:
        enabled, server = read_proxy_settings()
        if server and ":" in server:
            ip, port = server.split(":", 1)
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, ip)
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, port)
        if enabled:
            self.status_var.set(f"当前状态：已开启（{server or '未设置地址'}）")

    def refresh_status(self) -> None:
        enabled, server = read_proxy_settings()
        state = "已开启" if enabled else "已关闭"
        detail = server if server else "未设置代理地址"
        self.status_var.set(f"当前状态：{state}\n代理地址：{detail}")

    def enable_proxy(self) -> None:
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        server: str | None
        if ip or port:
            if not ip or not port:
                messagebox.showerror("输入错误", "请同时填写 IP 与端口，或都留空。")
                return
            if not port.isdigit():
                messagebox.showerror("输入错误", "端口必须是数字。")
                return
            server = f"{ip}:{port}"
        else:
            server = None

        try:
            set_proxy(True, server)
        except OSError as exc:
            messagebox.showerror("操作失败", f"无法开启代理：{exc}")
            return

        self.refresh_status()
        messagebox.showinfo("完成", "代理已开启。")

    def disable_proxy(self) -> None:
        try:
            set_proxy(False)
        except OSError as exc:
            messagebox.showerror("操作失败", f"无法关闭代理：{exc}")
            return

        self.refresh_status()
        messagebox.showinfo("完成", "代理已关闭。")


def main() -> None:
    root = tk.Tk()
    ProxySwitcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
