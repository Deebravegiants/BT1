# [?] fix: resolve potential deadlock in coinjoin_tests

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-02-22
Source: https://github.com/dashpay/dash/commit/2f5a466b9ea9b316588159065ae9186eeb8e3425
Type: security-commit

## Details
fix: resolve potential deadlock in coinjoin_tests

ScanForWalletTransactions should be called outside of cs_wallet lock scope

## Patch
### src/wallet/test/coinjoin_tests.cpp
```diff
@@ -139,11 +139,13 @@ class CTransactionBuilderTestSetup : public TestChain100Setup
             LOCK2(wallet->cs_wallet, cs_main);
             wallet->GetLegacyScriptPubKeyMan()->AddKeyPubKey(coinbaseKey, coinbaseKey.GetPubKey());
             wallet->SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
-            WalletRescanReserver reserver(*wallet);
-            reserver.reserve();
-            CWallet::ScanResult result = wallet->ScanForWalletTransactions(m_node.chainman->ActiveChain().Genesis()->GetBlockHash(),  0 /* start_height */, {} /* max_height */, reserver, true /* fUpdate */);
-            BOOST_CHECK_EQUAL(result.status, CWallet::ScanResult::SUCCESS);
         }
+        WalletRescanReserver reserver(*wallet);
+        reserver.reserve();
+        CWallet::ScanResult result = wallet->ScanForWalletTransactions(/*start_block=*/wallet->chain().getBlockHash(0),
+                                                                       /*start_height=*/0, /*max_height=*/{}, reserver,
+                                                                       /*fUpdate=*/true);
+        BOOST_CHECK_EQUAL(result.status, CWallet::ScanResult::SUCCESS);
     }
 
     ~CTransactionBuilderTestSetup()
```
