# [?] merge bitcoin-core/gui#835: Fix crash when closing wallet

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2024-09-12
Source: https://github.com/dashpay/dash/commit/20763f1101484fa1bbaa46c6aa9b3aa7766c11b2
Type: security-commit

## Details
merge bitcoin-core/gui#835: Fix crash when closing wallet

## Patch
### src/qt/walletcontroller.cpp
```diff
@@ -77,6 +77,14 @@ std::map<std::string, bool> WalletController::listWalletDir() const
     return wallets;
 }
 
+void WalletController::removeWallet(WalletModel* wallet_model)
+{
+    // Once the wallet is successfully removed from the node, the model will emit the 'WalletModel::unload' signal.
+    // This signal is already connected and will complete the removal of the view from the GUI.
+    // Look at 'WalletController::getOrCreateWallet' for the signal connection.
+    wallet_model->wallet().remove();
+}
+
 void WalletController::closeWallet(WalletModel* wallet_model, QWidget* parent)
 {
     QMessageBox box(parent);
@@ -87,10 +95,7 @@ void WalletController::closeWallet(WalletModel* wallet_model, QWidget* parent)
     box.setDefaultButton(QMessageBox::Yes);
     if (box.exec() != QMessageBox::Yes) return;
 
-    // First remove wallet from node.
-    wallet_model->wallet().remove();
-    // Now release the model.
-    removeAndDeleteWallet(wallet_model);
+    removeWallet(wallet_model);
 }
 
 void WalletController::closeAllWallets(QWidget* parent)
@@ -103,11 +108,8 @@ void WalletController::closeAllWallets(QWidget* parent)
 
     QMutexLocker locker(&m_mutex);
     for (WalletModel* wallet_model : m_wallets) {
-        wallet_model->wallet().remove();
-        Q_EMIT walletRemoved(wallet_model);
-        delete wallet_model;
+        removeWallet(wallet_model);
     }
-    m_wallets.clear();
 }
 
 WalletModel* WalletController::getOrCreateWallet(std::unique_ptr<interfaces::Wallet> wallet)
```

### src/qt/walletcontroller.h
```diff
@@ -82,6 +82,9 @@ class WalletController : public QObject
     std::unique_ptr<interfaces::Handler> m_handler_load_wallet;
 
     friend class WalletControllerActivity;
+
+    //! Starts the wallet closure procedure
+    void removeWallet(WalletModel* wallet_model);
 };
 
 class WalletControllerActivity : public QObject
```
