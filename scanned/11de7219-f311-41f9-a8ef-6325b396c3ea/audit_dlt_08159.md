# [?] Auto merge of #4687 - defuse:fix-cscript-test-buffer-overflows, r=daira

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2020-09-03
Source: https://github.com/zcash/zcash/commit/443954580dcd70324f67fd2cffa0ea91058b97f1
Type: security-commit

## Details
Auto merge of #4687 - defuse:fix-cscript-test-buffer-overflows, r=daira

Fix buffer overflows in P2PKH tests

## Patch
### src/test/script_P2PKH_tests.cpp
```diff
@@ -47,12 +47,12 @@ BOOST_AUTO_TEST_CASE(IsPayToPublicKeyHash)
     static const unsigned char missing2[] = {
         OP_DUP, OP_HASH160, 20, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
     };
-    BOOST_CHECK(!CScript(missing2, missing2+sizeof(missing)).IsPayToPublicKeyHash());
+    BOOST_CHECK(!CScript(missing2, missing2+sizeof(missing2)).IsPayToPublicKeyHash());
 
     static const unsigned char tooshort[] = {
         OP_DUP, OP_HASH160, 2, 0,0, OP_EQUALVERIFY, OP_CHECKSIG
     };
-    BOOST_CHECK(!CScript(tooshort, tooshort+sizeof(direct)).IsPayToPublicKeyHash());
+    BOOST_CHECK(!CScript(tooshort, tooshort+sizeof(tooshort)).IsPayToPublicKeyHash());
 
 }
 
```
