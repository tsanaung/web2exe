# Web2Exe 🚀

> Convert any Web Application or Website into a standalone Windows Desktop App (`.exe`) using Python, pywebview, and Microsoft Edge WebView2.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

---

## 🌟 Key Features

### 🖥️ Converter GUI (Builder Tool)
- **Dark Mode Modern Interface:** Clean, dark-themed Tkinter GUI for configuring and building apps.
- **Easy Configuration:** Set custom App Name, Start URL, and Application Icon with just a few clicks.
- **Dynamic Custom Menus:** Add custom menu rows linking to local HTML files (documentation, offline guides, settings, etc.) with automatic icon and asset bundling.
- **Automatic Icon Conversion:** Accepts `.png` icons and automatically generates `.ico` formats using Pillow for Windows compilation.

### 📦 Generated Desktop Application
- **Modern Edge WebView2 Engine:** Full support for modern HTML5, ES6+ JavaScript, CSS grid/flexbox, WebSockets, and PWA capabilities.
- **Custom Top Navigation Bar:**
  - Built-in `Home`, `Back`, `Forward`, `Reload`, and `New Tab` buttons.
  - Dropdown menu support to load custom local HTML pages in separate windows.
  - Collapsible toggle (`▲` / `▼`) to show or hide the navigation bar anytime.
- **Enhanced Right-Click Context Menu:**
  - Custom dark-themed context menu with navigation (`Back`, `Forward`, `Reload`).
  - Clipboard actions (`Copy`, `Paste`, `Select All`).
  - Link options (`Open in new tab`, `Open in new window`, `Copy link address`).
  - Forced text selection enabled (even on websites with CSS selection restrictions).
- **Persistent Storage & Offline Support:**
  - `localStorage`, `cookies`, `IndexedDB`, and cache persist across app restarts (stored in Windows `%LOCALAPPDATA%`).
  - PWA service worker support for offline usage.
- **Authentication & Popups:**
  - Google, Facebook, and Microsoft OAuth popups open in dedicated app windows.
  - External links (`mailto:`, `tel:`) open smoothly in the default system browser.
- **Native File Handling:** Built-in support for web file uploads and file downloads.

---

## 📋 Prerequisites

Before running the converter or compiling generated apps, ensure you have:

1. **Python 3.8+** installed on Windows.
2. **Microsoft Edge WebView2 Runtime** (installed by default on Windows 10 and 11; downloadable [here](https://developer.microsoft.com/microsoft-edge/webview2/) if missing).

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tsanaung/web2exe.git
   cd web2exe
