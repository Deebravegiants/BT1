# [?] qt: Fix potential crash due to mis-use of showProgress

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-03-29
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/93805bae3ba896216e7acfbe13c10dc2bb1c9dac
Type: security-commit

## Details
qt: Fix potential crash due to mis-use of showProgress

Summary
---

This fixes #485.  I traced the issue to the face that `100` was being
sent twice when importing a wallet.  The first time, the progress dialog
is deleted, but the pointer is never set to nullptr.  The second time,
the dangling pointer refers to deleted memory, and UB happens.

This commit fixes this by just enforcing invariants more strictly and
"doing the right thing".

When testing with this MR, I added extra debug prints to verify this was
the issue and this is what I got, verifying that the app no longer
crashes and invariants are respected:

    2023-03-29T12:10:28Z [default wallet] Rescan started from block 0000000066ff29c5752e769ee1a60627eebd40f36d55576c7a83b8e5505daaa6...
    2023-03-29T12:10:28Z !! shotProgress: 100, p = 0x0
    2023-03-29T12:10:28Z !! shotProgress: 100, p = 0x0

Test Plan
---

- `ninja check-all`
- Attempt to reproduce #485 both with and without this fix, and observe
  that this fix works and doesn't lead to an app crash.

## Patch
### src/qt/bitcoingui.cpp
```diff
@@ -39,6 +39,7 @@
 #include <ui_interface.h>
 #include <util/system.h>
 
+#include <algorithm>
 #include <memory>
 
 #include <QAction>
@@ -1411,20 +1412,20 @@ void BitcoinGUI::detectShutdown() {
 }
 
 void BitcoinGUI::showProgress(const QString &title, int nProgress) {
-    if (nProgress == 0) {
-        progressDialog = new QProgressDialog(title, "", 0, 100);
-        progressDialog->setWindowModality(Qt::ApplicationModal);
-        progressDialog->setMinimumDuration(0);
-        progressDialog->setCancelButton(nullptr);
-        progressDialog->setAutoClose(false);
-        progressDialog->setValue(0);
-    } else if (progressDialog) {
-        if (nProgress == 100) {
-            progressDialog->close();
-            progressDialog->deleteLater();
-        } else {
-            progressDialog->setValue(nProgress);
+    nProgress = std::clamp(nProgress, 0, 100); // ensure valid range
+    if (nProgress < 100) { // creation & normal usage for any value <100
+        if (!progressDialog) {
+            progressDialog = new QProgressDialog(title, "", 0, 100);
+            progressDialog->setWindowModality(Qt::ApplicationModal);
+            progressDialog->setMinimumDuration(0);
+            progressDialog->setCancelButton(nullptr);
+            progressDialog->setAutoClose(false);
         }
+        progressDialog->setValue(nProgress);
+    } else if (progressDialog) { // nProgress >= 100, delete progressDialog
+        progressDialog->close();
+        progressDialog->deleteLater();
+        progressDialog = nullptr;
     }
 }
 
```

### src/qt/bitcoingui.h
```diff
@@ -309,7 +309,10 @@ public Q_SLOTS:
     /** called by a timer to check if ShutdownRequested() has been set **/
     void detectShutdown();
 
-    /** Show progress dialog e.g. for verifychain */
+    /** Show progress dialog e.g. for verifychain
+     *  Calling this method for values <100 will create a new dialog if it
+     *  doesn't exist, or update the existing dialog if it does.
+     *  When nProgress >= 100 any existing dialog is closed & deleted. */
     void showProgress(const QString &title, int nProgress);
 
     /** When hideTrayIcon setting is changed in OptionsModel hide or show the
```
