# web2exe
Convert webapp to windows app (.exe) written in python.

Features: 

## Usage 
1. Clone the repo 
```shell
 https://github.com/tsanaung/web2exe.git
```
```shell
 cd web2exe
```
2. Prepairation
```shell
 pip install pywebview pyinstaller
```
3. Run web2exe.py (wit GUI)
```shell
 python web2exe.py
```
. Fill required fields and add some menu items.
. Generate

4. Test the generated app
```shell
 cd path-to-project-folder/<appName>/
```
```shell
 python app.py
```
5. Generate app
```shell
 pyinstaller --noconfirm --onefile --windowed --icon=assets/icon.ico --add-data "menu.json;." --add-data "menu;menu" --add-data "assets;assets" app.py
```
6. Use & share your work
