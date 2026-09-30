# [?] consensus: cache the openssl EC_GROUP to avoid a race condition for each CECKey instantiation

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-08-18
Source: https://github.com/dogecoin/dogecoin/commit/1d1073c2d3231a9de4adbc2bc46846fc20b34f9e
Type: security-commit

## Details
consensus: cache the openssl EC_GROUP to avoid a race condition for each CECKey instantiation

## Patch
### src/ecwrapper.cpp
```diff
@@ -13,6 +13,29 @@
 
 namespace {
 
+class ecgroup_order
+{
+public:
+  static const EC_GROUP* get()
+  {
+      static const ecgroup_order wrapper;
+      return wrapper.pgroup;
+  }
+
+private:
+  ecgroup_order()
+  : pgroup(EC_GROUP_new_by_curve_name(NID_secp256k1))
+  {
+  }
+
+  ~ecgroup_order()
+  {
+    EC_GROUP_free(pgroup);
+  }
+
+  EC_GROUP* pgroup;
+};
+
 /**
  * Perform ECDSA key recovery (see SEC1 4.1.6) for curves over (mod p)-fields
  * recid selects which key is recovered
@@ -92,8 +115,10 @@ int ECDSA_SIG_recover_key_GFp(EC_KEY *eckey, ECDSA_SIG *ecsig, const unsigned ch
 } // anon namespace
 
 CECKey::CECKey() {
-    pkey = EC_KEY_new_by_curve_name(NID_secp256k1);
+    pkey = EC_KEY_new();
     assert(pkey != NULL);
+    int result = EC_KEY_set_group(pkey, ecgroup_order::get());
+    assert(result);
 }
 
 CECKey::~CECKey() {
@@ -185,11 +210,9 @@ bool CECKey::TweakPublic(const unsigned char vchTweak[32]) {
 
 bool CECKey::SanityCheck()
 {
-    EC_KEY *pkey = EC_KEY_new_by_curve_name(NID_secp256k1);
-    if(pkey == NULL)
+    const EC_GROUP *pgroup = ecgroup_order::get();
+    if(pgroup == NULL)
         return false;
-    EC_KEY_free(pkey);
-
     // TODO Is there more EC functionality that could be missing?
     return true;
 }
```
