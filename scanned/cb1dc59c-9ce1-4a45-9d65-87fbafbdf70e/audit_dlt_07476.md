# [?] Merge #6593: fix: resolve potential deadlock in coinjoin_tests

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-02-23
Source: https://github.com/dashpay/dash/commit/f6163a2cfb345490eeec6c50f2ec8ad4c2c25456
Type: security-commit

## Details
Merge #6593: fix: resolve potential deadlock in coinjoin_tests

2f5a466b9ea9b316588159065ae9186eeb8e3425 fix: resolve potential deadlock in coinjoin_tests (UdjinM6)

Pull request description:

  ## Issue being fixed or feature implemented
  `ScanForWalletTransactions` should be called outside of `cs_wallet` lock scope which is not the case for `CTransactionBuilderTestSetup ` ctor in `coinjoin_tests.cpp` atm.

  Should fix tsan test failures like https://github.com/PastaPastaPasta/dash/actions/runs/13467587625/job/37636500963#step:8:1.

  ## What was done?

  ## How Has This Been Tested?

  ## Breaking Changes

  ## Checklist:
  - [ ] I have performed a self-review of my own code
  - [ ] I have commented my code, particularly in hard-to-understand areas
  - [ ] I have added or updated relevant unit/integration/functional/e2e tests
  - [ ] I have made corresponding changes to the documentation
  - [ ] I have assigned this pull request to a milestone _(for repository code-owners and collaborators only)_

ACKs for top commit:
  PastaPastaPasta:
    utACK 2f5a466b9ea9b316588159065ae9186eeb8e3425; thanks for looking into it!
  kwvg:
    utACK 2f5a466b9ea9b316588159065ae9186eeb8e3425

Tree-SHA512: 06a3b5d8406d6675f1a9271618dbb5b5839983b90c50c8895fce755639c8f90608748c5e5f56aecd8640420b15536c9e0b4d065b8b32eb6a2f3f731f132f1b59

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
