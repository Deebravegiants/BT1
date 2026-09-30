# [?] Fix buffer overflows in P2PKH tests

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2020-08-26
Source: https://github.com/zcash/zcash/commit/9f284b5010a8441e51a7f4843de0651dc3bd585a
Type: security-commit

## Details
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
