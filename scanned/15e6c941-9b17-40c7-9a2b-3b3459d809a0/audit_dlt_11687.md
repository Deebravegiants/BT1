# [?] qml: crash reporter: fix "show never" option

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2023-03-29
Source: https://github.com/spesmilo/electrum/commit/d189fdce69e445dd26585fbe1613ac2edb10b3bc
Type: security-commit

## Details
qml: crash reporter: fix "show never" option

102.82 | E | gui.qml.qeapp.Exception_Hook | exception caught by crash reporter
Traceback (most recent call last):
  File "/home/user/wspace/electrum/electrum/gui/qml/qeapp.py", line 271, in showNever
    self.config.set_key(BaseCrashReporter.config_key, False)
AttributeError: 'QEAppController' object has no attribute 'config'

## Patch
### electrum/gui/qml/qeapp.py
```diff
@@ -6,7 +6,7 @@
 import html
 import threading
 import asyncio
-from typing import TYPE_CHECKING
+from typing import TYPE_CHECKING, Set
 
 from PyQt5.QtCore import (pyqtSlot, pyqtSignal, pyqtProperty, QObject, QUrl, QLocale,
                           qInstallMessageHandler, QTimer, QSortFilterProxyModel)
@@ -58,12 +58,13 @@ class QEAppController(BaseCrashReporter, QObject):
     sendingBugreportSuccess = pyqtSignal(str)
     sendingBugreportFailure = pyqtSignal(str)
 
-    def __init__(self, qedaemon, plugins):
+    def __init__(self, qedaemon: 'QEDaemon', plugins: 'Plugins'):
         BaseCrashReporter.__init__(self, None, None, None)
         QObject.__init__(self)
 
         self._qedaemon = qedaemon
         self._plugins = plugins
+        self.config = qedaemon.daemon.config
 
         self._crash_user_text = ''
         self._app_started = False
```
