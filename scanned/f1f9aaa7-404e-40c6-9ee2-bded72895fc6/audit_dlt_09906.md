# [?] Upgrade axios to fix  CVE-2021-3749 (#874)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-01-13
Source: https://github.com/iron-fish/ironfish/commit/fa163cd2e7412747cb40088e92a664034e24a313
Type: security-commit

## Details
Upgrade axios to fix  CVE-2021-3749 (#874)

## Patch
### ironfish-cli/package.json
```diff
@@ -46,7 +46,7 @@
     "@oclif/config": "1.17.0",
     "@oclif/plugin-help": "3.2.2",
     "@oclif/plugin-not-found": "1.2.4",
-    "axios": "0.21.1",
+    "axios": "0.21.4",
     "blessed": "0.1.81",
     "cli-ux": "^5.5.0",
     "ironfish": "*",
```

### ironfish/package.json
```diff
@@ -8,7 +8,7 @@
   "license": "MPL-2.0",
   "dependencies": {
     "@napi-rs/blake-hash": "1.3.1",
-    "axios": "0.21.1",
+    "axios": "0.21.4",
     "bfilter": "1.0.5",
     "blru": "0.1.6",
     "buffer": "6.0.3",
```

### package.json
```diff
@@ -57,7 +57,7 @@
     "typescript": "4.3.4"
   },
   "resolutions": {
-    "axios": "0.21.1",
+    "axios": "0.21.4",
     "color-string": "1.5.5",
     "handlebars": "4.7.7",
     "node-notifier": "8.0.1",
```

### yarn.lock
```diff
@@ -2410,12 +2410,12 @@ aws4@^1.8.0:
   resolved "https://registry.yarnpkg.com/aws4/-/aws4-1.11.0.tgz#d61f46d83b2519250e2784daf5b09479a8b41c59"
   integrity sha512-xh1Rl34h6Fi1DC2WWKfxUTVqRsNnr6LsKz2+hfwDxQJWmrx8+c7ylaqBMcHfl1U1r2dsifOvKX3LQuLNZ+XSvA==
 
-axios@0.21.1, axios@^0.21.1:
-  version "0.21.1"
-  resolved "https://registry.yarnpkg.com/axios/-/axios-0.21.1.tgz#22563481962f4d6bde9a76d516ef0e5d3c09b2b8"
-  integrity sha512-dKQiRHxGD9PPRIUNIWvZhPTPpl1rf/OxTYKsqKUDjBwYylTvV7SjSHJb9ratfyzM6wCdLCOYLzs73qpg5c4iGA==
+axios@0.21.4, axios@^0.21.1:
+  version "0.21.4"
+  resolved "https://registry.yarnpkg.com/axios/-/axios-0.21.4.tgz#c67b90dc0568e5c1cf2b0b858c43ba28e2eda575"
+  integrity sha512-ut5vewkiu8jjGBdqpM44XxjuCjq9LAKeHVmoVfHVzy8eHgxxq8SbAVQNovDA8mVi05kP0Ea/n/UzcSHcTJQfNg==
   dependencies:
-    follow-redirects "^1.10.0"
+    follow-redirects "^1.14.0"
 
 babel-jest@^26.6.3:
   version "26.6.3"
@@ -4576,10 +4576,10 @@ fn-name@~3.0.0:
   resolved "https://registry.yarnpkg.com/fn-name/-/fn-name-3.0.0.tgz#0596707f635929634d791f452309ab41558e3c5c"
   integrity sha512-eNMNr5exLoavuAMhIUVsOKF79SWd/zG104ef6sxBTSw+cZc6BXdQXDvYcGvp0VbxVVSp1XDUNoz7mg1xMtSznA==
 
-follow-redirects@^1.10.0:
-  version "1.14.5"
-  resolved "https://registry.yarnpkg.com/follow-redirects/-/follow-redirects-1.14.5.tgz#f09a5848981d3c772b5392309778523f8d85c381"
-  integrity sha512-wtphSXy7d4/OR+MvIFbCVBDzZ5520qV8XfPklSN5QtxuMUJZ+b0Wnst1e1lCDocfzuCkHqj8k0FpZqO+UIaKNA==
+follow-redirects@^1.14.0:
+  version "1.14.7"
+  resolved "https://registry.yarnpkg.com/follow-redirects/-/follow-redirects-1.14.7.tgz#2004c02eb9436eee9a21446a6477debf17e81685"
+  integrity sha512-+hbxoLbFMbRKDwohX8GkTataGqO6Jb7jGwpAlwgy2bIz25XtRm7KEzJM76R1WiNT5SwZkX4Y75SwBolkpmE7iQ==
 
 for-in@^1.0.2:
   version "1.0.2"
```
