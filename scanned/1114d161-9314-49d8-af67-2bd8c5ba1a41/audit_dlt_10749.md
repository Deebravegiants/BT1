# [?] gui: fix crash when closing wallet

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-09-12
Source: https://github.com/ElementsProject/elements/commit/a965f2bc07a3588f8c2b8d6a542961562e3f5d0e
Type: security-commit

## Details
gui: fix crash when closing wallet

The crash occurs because 'WalletController::removeAndDeleteWallet' is called
twice for the same wallet model: first in the GUI's button connected function
'WalletController::closeWallet', and then again when the backend emits the
'WalletModel::unload' signal.

This causes the issue because 'removeAndDeleteWallet' inlines an
erase(std::remove()). So, if 'std::remove' returns an iterator to the end
(indicating the element wasn't found because it was already erased), the
subsequent call to 'erase' leads to an undefined behavior.

## Patch
### src/qt/walletcontroller.cpp
```diff
@@ -79,6 +79,14 @@ std::map<std::string, std::pair<bool, std::string>> WalletController::listWallet
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
@@ -89,10 +97,7 @@ void WalletController::closeWallet(WalletModel* wallet_model, QWidget* parent)
     box.setDefaultButton(QMessageBox::Yes);
     if (box.exec() != QMessageBox::Yes) return;
 
-    // First remove wallet from node.
-    wallet_model->wallet().remove();
-    // Now release the model.
-    removeAndDeleteWallet(wallet_model);
+    removeWallet(wallet_model);
 }
 
 void WalletController::closeAllWallets(QWidget* parent)
@@ -105,11 +110,8 @@ void WalletController::closeAllWallets(QWidget* parent)
 
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
@@ -85,6 +85,9 @@ class WalletController : public QObject
 
     friend class WalletControllerActivity;
     friend class MigrateWalletActivity;
+
+    //! Starts the wallet closure procedure
+    void removeWallet(WalletModel* wallet_model);
 };
 
 class WalletControllerActivity : public QObject
```
