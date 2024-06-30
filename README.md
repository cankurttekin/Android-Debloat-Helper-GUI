# GUI Tool to Debloat Android Phones with ADB Shell
This GUI tool will let you uninstall any apps incluing spyware/data selling/full of ads system apps without root.
<p>
  <img height="500" width="" src="/assets/screenshot.png">
</p>

## Usage
- Open developer settings on your Android phone.
- Connect your device to your pc with usb cable(if you dont want to use cable you may need additional permissions for adb shell commands with wireless debugging depending on manufacturer)
- Run either "python android-debloat-helper.py", "python3 android-debloat-helper.py" depending at your python path configuration.
- Click connect. Make sure the device is the one you want to work on.
- Click refresh to see packages.
- You can select multiple packages and uninstall at once or use search bar to find your package and uninstall it.
- If you want to restore app you can click restore button and put your package name and it will install it back.

## ⚠️ WARNING:  Research each package before uninstalling. Some apps may have dependencies and may break how your system works.
This won't brick your phone but it may cause unwanted behaviors or unable to navigate through phone. So you will have to restore each package that cause this issue or you may have to wipe your phone(with data loss if you dont backup)
<br>
In my own experience removing launcher or gallery on MIUI phone messed up my third party launchers and i had to reinstall those packages.
<br>
Use at your own risk. 

## Demo
![til](/assets/demo.gif)
