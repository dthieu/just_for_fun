# ISSUE
## Numpy version inapproriate
About the function "Convert to mp3 file", there is an error may occurs 
when installing "moviepy" by pip command. The version of numpy which 
installed during install moviepy maybe conflick with another library.
It leads to errors when runing app. After install package "moviepy", 
just re-install numpy by below command to fix this issue:
```bash
$ pip install numpy==1.19.3 # moviepy + app work correctly with this version
```

