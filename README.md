This program allows you to control your android device via a slow internet connection via adb, no need to install any apps or extra packages.

If you have a fast internet connection, you can use VNC or similar which only sends you the "differences" between each image, but it doesn't let you choose how often the images are sent which will be jerky with a slow internet connection.


## To install...

```
git clone https://github.com/niknah/AndroidViaWeb.git

# Install the Android sdk and make sure "adb" is in your path.
export PATH:$PATH:~/Android/Sdk/platform-tools/

pip install culebratester-client

git clone https://github.com/dtmilano/AndroidViewClient.git

# Turn on usb debugging on the Android device, plug it into the usb and run...
python AndroidViaWeb.py
```

Go to your web browser and look at http://localhost:8080/

If you have multiple Android devices plugged in, use...
python AndroidViaWeb.py --serial=xxxx

For better screen quality...
python AndroidViaWeb.py --imageFormat=PNG

Different port...
python AndroidViaWeb.py --port=8081


## Issues
* It only supports swiping in a straight line.  ie. You won't be able to unlock a swipe screen lock.
* It doesn't support hold and drag.  ie. You won't be able hold and drag to uninstall/move an app.  Use "adb uninstall xxx" instead.

