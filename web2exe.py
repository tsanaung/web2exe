# -*- coding: utf-8 -*-
"""
webapp2win.py
--------------
Web App ကို Windows Desktop App အဖြစ် ပြောင်းပေးတဲ့ Converter GUI (tkinter)

Features:
  - App name ထည့်စရာ text field
  - Web app link ထည့်စရာ text field
  - icon.png ရွေးစရာ Browse button
  - Menu item တွေ ထည့်စရာ (label + HTML file တစ်ခုချင်းစီ Browse)
  - Generate လုပ်တဲ့အခါ pywebview နဲ့ အလုပ်လုပ်တဲ့ Windows app project တစ်ခု ထုတ်ပေးမယ်
    (top navigation bar + menu dropdown + back/forward/reload/home/new tab
    + right-click context menu + text selection + upload/download အားလုံးပါ)

Run:
  pip install pywebview pyinstaller pillow
  python webapp2win.py
"""

import os
import re
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------------------------------------------------------------------------
# Templates for the GENERATED Windows app
# ---------------------------------------------------------------------------

TOPBAR_JS_TEMPLATE = r"""
(function () {
  if (window.__tbAdded) return; window.__tbAdded = true;
  var MENU = __MENU_ITEMS__;
  var visible = true;

  // ---- Top navigation bar (window border အပေါ်ဘက်မှာ) ----
  var bar = document.createElement('div');
  bar.id = '__app_topbar__';
  bar.setAttribute('style', 'position:fixed;top:0;left:0;right:0;height:44px;background:#111827;color:#e5e7eb;z-index:2147483647;display:flex;align-items:center;gap:6px;padding:0 10px;font-family:Segoe UI,Arial,sans-serif;box-shadow:0 1px 6px rgba(0,0,0,.35);');

  var title = document.createElement('span');
  title.setAttribute('style', 'font-weight:bold;font-size:13px;color:#9ca3af;margin-right:10px;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;');
  title.textContent = '__APP_NAME__';
  bar.appendChild(title);

  function mkBtn(text, tip, fn) {
    var b = document.createElement('button');
    b.textContent = text;
    b.title = tip;
    b.setAttribute('style', 'background:#1f2937;color:#e5e7eb;border:none;border-radius:6px;cursor:pointer;font-size:13px;padding:7px 11px;');
    b.onmouseenter = function () { b.style.background = '#374151'; };
    b.onmouseleave = function () { b.style.background = '#1f2937'; };
    b.onclick = fn;
    bar.appendChild(b);
    return b;
  }

  mkBtn('Home', 'Home', function () { window.location.href = '__START_URL__'; });
  mkBtn('Back', 'Back', function () { history.back(); });
  mkBtn('Forward', 'Forward', function () { history.forward(); });
  mkBtn('Reload', 'Reload', function () { location.reload(); });
  mkBtn('New Tab', 'Open new tab', function () { pywebview.api.open_tab(); });

  // ---- Menu dropdown ----
  var menuWrap = document.createElement('div');
  menuWrap.setAttribute('style', 'position:relative;margin-left:8px;');
  var menuBtn = document.createElement('button');
  menuBtn.textContent = 'Menu \u25be';
  menuBtn.setAttribute('style', 'background:#1f2937;color:#e5e7eb;border:none;border-radius:6px;cursor:pointer;font-size:13px;padding:7px 11px;');
  menuBtn.onmouseenter = function () { menuBtn.style.background = '#374151'; };
  menuBtn.onmouseleave = function () { menuBtn.style.background = '#1f2937'; };
  var dd = document.createElement('div');
  dd.setAttribute('style', 'display:none;position:absolute;top:42px;left:0;background:#1f2937;border-radius:8px;min-width:180px;box-shadow:0 6px 20px rgba(0,0,0,.5);padding:6px 0;z-index:2147483647;');
  MENU.forEach(function (m, i) {
    var it = document.createElement('div');
    it.textContent = m[0];
    it.setAttribute('style', 'padding:8px 14px;cursor:pointer;font-size:13px;');
    it.onmouseenter = function () { it.style.background = '#374151'; };
    it.onmouseleave = function () { it.style.background = 'transparent'; };
    it.onclick = function () { dd.style.display = 'none'; pywebview.api.open_menu(i); };
    dd.appendChild(it);
  });
  menuBtn.onclick = function (e) {
    e.stopPropagation();
    dd.style.display = dd.style.display === 'block' ? 'none' : 'block';
  };
  menuWrap.appendChild(menuBtn);
  menuWrap.appendChild(dd);
  bar.appendChild(menuWrap);
  document.addEventListener('click', function () { dd.style.display = 'none'; });

  // ---- Show / hide bar ----
  var toggle = document.createElement('button');
  toggle.textContent = '\u25b2';
  toggle.title = 'Show / Hide navigation bar';
  toggle.setAttribute('style', 'position:fixed;top:48px;left:10px;z-index:2147483647;background:#111827;color:#fff;border:none;border-radius:4px;width:26px;height:26px;cursor:pointer;font-size:12px;');
  toggle.onclick = function () {
    visible = !visible;
    bar.style.display = visible ? 'flex' : 'none';
    toggle.textContent = visible ? '\u25b2' : '\u25bc';
  };

  document.body.appendChild(bar);
  document.body.appendChild(toggle);
})();
"""

CONTEXT_MENU_JS_TEMPLATE = r"""
(function () {
  if (window.__cmAdded) return; window.__cmAdded = true;

  // Text selection က WebView2 မှာ default အတိုင်း အလုပ်လုပ်ပါတယ်။
  // CSS နဲ့ ပိတ်ထားတဲ့ site တွေအတွက် force enable လုပ်ပေးမယ်။
  var st = document.createElement('style');
  st.textContent = '*{-webkit-user-select:text !important;user-select:text !important;}';
  document.head.appendChild(st);

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
  }

  // ---- Third-party auth / popups ----
  // window.open (Google/Facebook/Microsoft sign-in popup တွေ) ကို
  // app ရဲ့ new window တစ်ခုအဖြစ် ပြောင်းဖွင့်ပေးမယ်။
  window.open = function (u) {
    if (u) { try { pywebview.api.open_popup(String(u)); } catch (err) {} }
    return null;
  };

  // ---- target="_blank" link တွေကို new tab မှာ ဖွင့်ပေးမယ် ----
  // mailto:/tel: တွေက system browser နဲ့ ဖွင့်ပေးမယ်။
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a || !a.href) return;
    if (a.target === '_blank') {
      e.preventDefault();
      pywebview.api.open_tab_url(String(a.href));
    } else if (/^(mailto|tel):/i.test(a.protocol)) {
      e.preventDefault();
      pywebview.api.open_external(String(a.href));
    }
  }, true);

  // ---- Right-click context menu ----
  document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    var old = document.getElementById('__app_ctxmenu__');
    if (old) old.remove();

    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    var hasLink = !!(a && a.href && /^https?:/i.test(a.href));

    var cm = document.createElement('div');
    cm.id = '__app_ctxmenu__';
    cm.setAttribute('style', 'position:fixed;z-index:2147483647;background:#1f2937;color:#e5e7eb;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.5);min-width:180px;padding:6px 0;font-family:Segoe UI,Arial,sans-serif;font-size:13px;');

    function mi(text, fn) {
      var it = document.createElement('div');
      it.textContent = text;
      it.setAttribute('style', 'padding:8px 14px;cursor:pointer;');
      it.onmouseenter = function () { it.style.background = '#374151'; };
      it.onmouseleave = function () { it.style.background = 'transparent'; };
      it.onclick = function () { cm.remove(); fn(); };
      cm.appendChild(it);
    }
    function sep() {
      var s = document.createElement('div');
      s.setAttribute('style', 'border-top:1px solid #374151;margin:4px 0;');
      cm.appendChild(s);
    }

    // Hyperlink ပေါ်မှာ right click လုပ်ရင် ဒီ item တွေ ပေါ်မယ်
    if (hasLink) {
      mi('Open in new tab', function () { pywebview.api.open_tab_url(String(a.href)); });
      mi('Open in new window', function () { pywebview.api.open_window_url(String(a.href)); });
      mi('Copy link address', function () { copyText(String(a.href)); });
      sep();
    }

    mi('Back', function () { history.back(); });
    mi('Forward', function () { history.forward(); });
    mi('Reload', function () { location.reload(); });
    sep();
    mi('Select All', function () { document.execCommand('selectAll'); });
    mi('Copy', function () { document.execCommand('copy'); });
    mi('Paste', function () { document.execCommand('paste'); });

    cm.style.left = Math.min(e.clientX, window.innerWidth - 190) + 'px';
    cm.style.top = Math.min(e.clientY, window.innerHeight - 260) + 'px';
    document.body.appendChild(cm);
  });

  document.addEventListener('click', function (e) {
    var cm = document.getElementById('__app_ctxmenu__');
    if (cm && !cm.contains(e.target)) cm.remove();
  });
})();
"""

APP_TEMPLATE = r'''# -*- coding: utf-8 -*-
"""
__APP_NAME__ - Windows Desktop App
Generated by webapp2win

Test run:
    pip install pywebview
    python app.py

Build .exe:
    pip install pyinstaller
    pyinstaller --noconfirm --onefile --windowed --icon=assets/icon.ico app.py
"""

import os
import re
import sys
import json
import webbrowser
import webview

APP_NAME = "__APP_NAME__"
START_URL = "__START_URL__"

# PyInstaller --onefile မှာ resource တွေက temp folder (_MEIPASS) ထဲ
# extract လုပ်ပါတယ်။ Persistent data ကိုတော့ EXE folder မဟုတ်ဘဲ
# user ရဲ့ writable AppData folder ထဲမှာ သိမ်းပါမယ်။
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_APP_DATA = os.environ.get(
    "LOCALAPPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Local")
)
DATA_DIR = os.path.join(LOCAL_APP_DATA, re.sub(r"[^A-Za-z0-9_.-]+", "_", APP_NAME).strip("._") or "MyApp")
WEBVIEW_DATA_DIR = os.path.join(DATA_DIR, "webview_data")
os.makedirs(WEBVIEW_DATA_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "menu.json"), "r", encoding="utf-8") as f:
    MENU = json.load(f)


class Api:
    """JS bridge: top bar menu + tabs + popups အတွက်"""

    def open_menu(self, index):
        label, rel = MENU[int(index)]
        path = os.path.join(BASE_DIR, rel)
        webview.create_window(label, "file:///" + path.replace("\\", "/"),
                              width=1024, height=720)
        return True

    def open_tab(self):
        webview.create_window(APP_NAME, START_URL, width=1200, height=800)
        return True

    def open_tab_url(self, url):
        webview.create_window(APP_NAME, url, width=1200, height=800)
        return True

    def open_window_url(self, url):
        webview.create_window("New Window", url, width=1000, height=700)
        return True

    def open_popup(self, url):
        # Third-party auth (Google/Facebook/...) sign-in popup window
        webview.create_window("Sign in", url, width=900, height=650)
        return True

    def open_external(self, url):
        webbrowser.open(url)
        return True


TOPBAR_JS = r"""__TOPBAR_JS__"""
CONTEXT_MENU_JS = r"""__CTXMENU_JS__"""


def inject_ui(window):
    try:
        window.evaluate_js(TOPBAR_JS)
        window.evaluate_js(CONTEXT_MENU_JS)
    except Exception:
        pass


if __name__ == "__main__":
    # private_mode ပိတ်ထားတာက localStorage / cookies / service worker
    # တွေကို app ပိတ်ပြီးပြန်ဖွင့်ရင်လည်း ဆက်ရှိနေအောင် လုပ်ပေးပါတယ်။
    # PWA (offline) app တွေအတွက်လည်း ဒါက အရေးကြီးပါတယ်။
    # (pywebview version အမျိုးမျိုးမှာ key တွေမတူလို့ စစ်ပြီး set လုပ်တာ)
    if "private_mode" in webview.settings:
        webview.settings["private_mode"] = False
    if "PRIVATE_MODE" in webview.settings:
        webview.settings["PRIVATE_MODE"] = False
    window = webview.create_window(APP_NAME, START_URL,
                                   width=1200, height=800, js_api=Api())
    window.events.loaded += lambda: inject_ui(window)
    # storage_path ကို တိတိကျကျ သတ်မှတ်ထားမှ WebView2 cookies,
    # localStorage, IndexedDB စတာတွေ app ပိတ်ပြီး ပြန်ဖွင့်လည်း ကျန်ပါမယ်။
    # TypeError ဖြစ်ရင် persistence မရတဲ့ version ဖြစ်နိုင်လို့
    # အမှားကို ဖုံးမထားဘဲ ပြသပါမယ်။
    # webview.start(storage_path=WEBVIEW_DATA_DIR)

    webview.start(
        private_mode=False,
        storage_path=WEBVIEW_DATA_DIR
    )
'''

README_TEMPLATE = r'''========================================
  __APP_NAME__ - Windows Desktop App
========================================

1) Test run
-----------
   pip install pywebview
   python app.py

2) Build single .exe
--------------------
   pip install pyinstaller
   pyinstaller --noconfirm --onefile --windowed --icon=assets/icon.ico --add-data "menu.json;." --add-data "menu;menu" --add-data "assets;assets" app.py

   -> dist\app.exe  ထဲမှာ ရပါမယ်။ icon.ico မရှိရင် --icon=assets/icon.png ကို သုံးပါ။

Notes
-----
- Window အပေါ်ဘက် (top border) မှာ navigation bar ပါဝင်ပါတယ်:
  Home / Back / Forward / Reload / New Tab နဲ့ Menu dropdown (menu item တွေ)။
  Menu item တွေက menu\ folder ထဲက html file တွေကို new window မှာ ဖွင့်ပေးပါတယ်။
  Navigation bar ကို ▲/▼ နှိပ်ပြီး ပြ/ချောင်းလို့ရပါတယ်။
- Right-click လုပ်ရင် context menu (Back / Forward / Reload / Select All /
  Copy / Paste) ပေါ်ပါမယ်။ Text selection လည်း enable ထားပါတယ်။
- Hyperlink ပေါ်မှာ right-click လုပ်ရင် Open in new tab /
  Open in new window / Copy link address တွေ ပေါ်ပါမယ်။
- JavaScript, localStorage, cookies, IndexedDB, service workers တွေက
  WebView2 engine အပြည့်အစုံနဲ့ run ပါတယ်။ private_mode ပိတ်ထား
 လို့ app ပိတ်ပြန်ဖွင့်ရင် data တွေ ဆက်ရှိနေပါမယ် (user_data\ folder)။
- PWA (offline) app တွေ: site မှာ service worker ရှိရင် offline
  အလုပ်လုပ်ပါမယ်။ cache တွေက user_data\ folder ထဲ သိမ်းပါတယ်။
- Third-party auth (Google / Facebook / Microsoft sign-in popup တွေ)က
  app ရဲ့ new window မှာ ဖွင့်ပေးပါတယ်။ တချို့ auth provider တွေက popup
  အစား redirect flow ကို ပိုသုံးအားပေးပါတယ်။
- Upload (file picker) နဲ့ Download တွေက WebView2 browser engine ရဲ့
  built-in function အတိုင်း အလုပ်လုပ်ပါတယ်။
- Windows မှာ Microsoft Edge WebView2 Runtime လိုအပ်ပါတယ်
  (Windows 10/11 မှာ များသောအားဖြင့် ပါနေပါပြီ)။
  မရှိရင် https://developer.microsoft.com/microsoft-edge/webview2/ ကနေ download လုပ်ပါ။
'''


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def safe_name(name):
    return re.sub(r'[^\w\- ]+', '', name).strip().replace(' ', '_') or 'MyApp'


def normalize_url(url):
    url = url.strip()
    if url and not url.startswith(('http://', 'https://', 'file://')):
        url = 'https://' + url
    return url


def png_to_ico(png_path, ico_path):
    """Pillow ရှိရင် icon.png ကို icon.ico အဖြစ် ပြောင်းပေးမယ်"""
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class MenuRow:
    """Menu item တစ်ခုချင်းစီအတွက် row (label + html file)"""

    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', pady=2)

        self.label_var = tk.StringVar()
        self.path_var = tk.StringVar()

        ttk.Entry(self.frame, textvariable=self.label_var, width=20).pack(
            side='left', padx=(2, 4))
        ttk.Entry(self.frame, textvariable=self.path_var, width=42).pack(
            side='left', padx=4)
        ttk.Button(self.frame, text='Browse HTML', width=12,
                   command=self.browse).pack(side='left', padx=4)
        ttk.Button(self.frame, text='✕', width=3,
                   command=self.remove).pack(side='left', padx=2)

    def browse(self):
        path = filedialog.askopenfilename(
            filetypes=[('HTML files', '*.html *.htm'), ('All files', '*.*')])
        if path:
            self.path_var.set(path)
            if not self.label_var.get():
                self.label_var.set(
                    os.path.splitext(os.path.basename(path))[0])

    def remove(self):
        self.frame.destroy()
        if self in self.app.rows:
            self.app.rows.remove(self)


class ConverterApp(tk.Tk):
    def __init__(self):
        # Old Light Mode
        # super().__init__()
        # self.title('Web App → Windows App Converter')
        # self.geometry('780x640')
        # self.resizable(True, True)

        super().__init__()

        self.title('Web App → Windows App Converter')
        self.geometry('780x640')
        self.resizable(True, True)

        # DARK MODE THEME
        self.configure(bg='#111827')

        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure(
            '.',
            background='#111827',
            foreground='#f9fafb',
            fieldbackground='#1f2937',
            font=('Segoe UI', 10)
        )

        style.configure(
            'TFrame',
            background='#111827'
        )

        style.configure(
            'TLabel',
            background='#111827',
            foreground='#f9fafb'
        )

        style.configure(
            'TButton',
            background='#374151',
            foreground='#ffffff',
            padding=7,
            borderwidth=0
        )

        style.map(
            'TButton',
            background=[('active', '#4b5563')],
            foreground=[('active', '#ffffff')]
        )

        style.configure(
            'TEntry',
            fieldbackground='#1f2937',
            foreground='#ffffff',
            insertcolor='#ffffff'
        )

        style.configure(
            'Vertical.TScrollbar',
            background='#374151',
            troughcolor='#111827'
        )

        self.rows = []

        container = ttk.Frame(self, padding=12)
        container.pack(fill='both', expand=True)

        # ---- App name -------------------------------------------------
        ttk.Label(container, text='App Name:').grid(
            row=0, column=0, sticky='w', pady=3)
        self.name_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.name_var, width=50).grid(
            row=0, column=1, sticky='w', pady=3)

        # ---- Web app link --------------------------------------------
        ttk.Label(container, text='Web App Link (URL):').grid(
            row=1, column=0, sticky='w', pady=3)
        self.url_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.url_var, width=50).grid(
            row=1, column=1, sticky='w', pady=3)

        # ---- Icon -----------------------------------------------------
        ttk.Label(container, text='App Icon (icon.png):').grid(
            row=2, column=0, sticky='w', pady=3)
        icon_frame = ttk.Frame(container)
        icon_frame.grid(row=2, column=1, sticky='w', pady=3)
        self.icon_var = tk.StringVar()
        ttk.Entry(icon_frame, textvariable=self.icon_var, width=42).pack(
            side='left')
        ttk.Button(icon_frame, text='Browse', width=10,
                   command=self.browse_icon).pack(side='left', padx=4)

        # ---- Menu items -----------------------------------------------
        ttk.Label(container, text='Menu Items (label + HTML file):').grid(
            row=3, column=0, columnspan=2, sticky='w', pady=(14, 4))
        ttk.Button(container, text='＋ Add Menu Item',
                   command=self.add_row).grid(
            row=3, column=1, sticky='e', pady=(10, 4))

        rows_frame = ttk.Frame(container)
        rows_frame.grid(row=4, column=0, columnspan=2,
                        sticky='nsew', pady=4)

        self.canvas = tk.Canvas(rows_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(rows_frame, orient='vertical',
                                  command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor='nw')
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.itemconfigure(
                self.canvas_window, width=self.canvas.winfo_width()))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Mouse wheel scroll (Windows)
        self.canvas.bind_all(
            '<MouseWheel>',
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), 'units'))

        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

        # ---- Generate --------------------------------------------------
        self.generate_btn = ttk.Button(
            container, text='🚀 Generate Windows App Project',
            command=self.generate)
        self.generate_btn.grid(row=5, column=0, columnspan=2,
                               sticky='ew', pady=(12, 0))

        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(container, textvariable=self.status_var,
                  foreground='#555').grid(row=6, column=0, columnspan=2,
                                          sticky='w', pady=(6, 0))

        self.add_row()

    # ------------------------------------------------------------------
    def browse_icon(self):
        path = filedialog.askopenfilename(
            filetypes=[('PNG images', '*.png'), ('All files', '*.*')])
        if path:
            self.icon_var.set(path)

    def add_row(self):
        self.rows.append(MenuRow(self, self.scroll_frame))

    # ------------------------------------------------------------------
    def collect_menu_items(self):
        """[(label, html_path), ...] — ဒီလိုစု collect လုပ်မယ်"""
        items = []
        for row in self.rows:
            label = row.label_var.get().strip()
            path = row.path_var.get().strip()
            if label and path and os.path.isfile(path):
                items.append((label, path))
        return items

    def generate(self):
        app_name = self.name_var.get().strip()
        url = normalize_url(self.url_var.get())
        icon_png = self.icon_var.get().strip()
        menu_items = self.collect_menu_items()

        if not app_name:
            messagebox.showerror('Error', 'App Name ထည့်ပါ။')
            return
        if not url:
            messagebox.showerror('Error', 'Web App Link ထည့်ပါ။')
            return
        if icon_png and not os.path.isfile(icon_png):
            messagebox.showerror('Error', 'Icon PNG file ကို ပြန်ရွေးပါ။')
            return

        out_root = filedialog.askdirectory(title='Output folder ရွေးပါ')
        if not out_root:
            return

        try:
            project_dir = os.path.join(out_root, safe_name(app_name))
            os.makedirs(os.path.join(project_dir, 'assets'), exist_ok=True)
            os.makedirs(os.path.join(project_dir, 'menu'), exist_ok=True)

            # icon
            if icon_png:
                shutil.copy(icon_png,
                            os.path.join(project_dir, 'assets', 'icon.png'))
                png_to_ico(icon_png,
                           os.path.join(project_dir, 'assets', 'icon.ico'))

            # menu html files + menu.json
            menu_json = []
            for i, (label, html_path) in enumerate(menu_items):
                fname = f'menu_{i + 1}_{safe_name(os.path.splitext(os.path.basename(html_path))[0])}.html'
                shutil.copy(html_path, os.path.join(project_dir, 'menu', fname))
                menu_json.append([label, f'menu/{fname}'])
            with open(os.path.join(project_dir, 'menu.json'), 'w',
                      encoding='utf-8') as f:
                json.dump(menu_json, f, ensure_ascii=False, indent=2)

            # top bar + context menu JS
            topbar_js = (TOPBAR_JS_TEMPLATE
                         .replace('__MENU_ITEMS__', json.dumps(menu_json))
                         .replace('__APP_NAME__', app_name)
                         .replace('__START_URL__', url))

            # app.py
            app_code = (APP_TEMPLATE
                        .replace('__APP_NAME__', app_name)
                        .replace('__START_URL__', url)
                        .replace('__TOPBAR_JS__', topbar_js)
                        .replace('__CTXMENU_JS__', CONTEXT_MENU_JS_TEMPLATE))
            with open(os.path.join(project_dir, 'app.py'), 'w',
                      encoding='utf-8') as f:
                f.write(app_code)

            # README
            with open(os.path.join(project_dir, 'README.txt'), 'w',
                      encoding='utf-8') as f:
                f.write(README_TEMPLATE.replace('__APP_NAME__', app_name))

            self.status_var.set(f'Generated: {project_dir}')
            messagebox.showinfo(
                'Success',
                'Project ထုတ်ပြီးပါပြီ!\n\n'
                f'{project_dir}\n\n'
                'Test:  pip install pywebview  ပြီးရင်  python app.py\n'
                'Build: pip install pyinstaller  ပြီးရင်\n'
                'pyinstaller --noconfirm --onefile --windowed '
                '--icon=assets/icon.ico app.py')

        except Exception as e:
            messagebox.showerror('Error', f'Generate မအောင်မြင်ပါ:\n{e}')


if __name__ == '__main__':
    app = ConverterApp()
    app.mainloop()