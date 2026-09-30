# [?] gui: Fix SplashScreen crash when run with -disablewallet

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-10-09
Source: https://github.com/litecoin-project/litecoin/commit/c056064a4a93be3601a63b37afea41f8b878df79
Type: security-commit

## Details
gui: Fix SplashScreen crash when run with -disablewallet

## Patch
### src/qt/splashscreen.cpp
```diff
@@ -14,6 +14,7 @@
 #include <interfaces/wallet.h>
 #include <qt/guiutil.h>
 #include <qt/networkstyle.h>
+#include <qt/walletmodel.h>
 #include <util/system.h>
 #include <util/translation.h>
 
@@ -196,6 +197,7 @@ void SplashScreen::subscribeToCoreSignals()
 void SplashScreen::handleLoadWallet()
 {
 #ifdef ENABLE_WALLET
+    if (!WalletModel::isWalletEnabled()) return;
     m_handler_load_wallet = m_node->walletClient().handleLoadWallet([this](std::unique_ptr<interfaces::Wallet> wallet) {
         m_connected_wallet_handlers.emplace_back(wallet->handleShowProgress(std::bind(ShowProgress, this, std::placeholders::_1, std::placeholders::_2, false)));
         m_connected_wallets.emplace_back(std::move(wallet));
```
