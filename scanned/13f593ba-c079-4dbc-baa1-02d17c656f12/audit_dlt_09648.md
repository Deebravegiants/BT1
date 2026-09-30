# [?] Fix segfault crash when shutdown the GUI in disablewallet mode

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-02-21
Source: https://github.com/dogecoin/dogecoin/commit/7d75a5a93c161aa4de22ac862702ba0241e8faa2
Type: security-commit

## Details
Fix segfault crash when shutdown the GUI in disablewallet mode

Github-Pull: #9817
Rebased-From: 312c4f10574ccf6dfe0d4ecb3ce928733d3a1e52

## Patch
### src/qt/bitcoingui.cpp
```diff
@@ -518,7 +518,10 @@ void BitcoinGUI::setClientModel(ClientModel *_clientModel)
         // Propagate cleared model to child objects
         rpcConsole->setClientModel(nullptr);
 #ifdef ENABLE_WALLET
-        walletFrame->setClientModel(nullptr);
+        if (walletFrame)
+        {
+            walletFrame->setClientModel(nullptr);
+        }
 #endif // ENABLE_WALLET
         unitDisplayControl->setOptionsModel(nullptr);
     }
```
