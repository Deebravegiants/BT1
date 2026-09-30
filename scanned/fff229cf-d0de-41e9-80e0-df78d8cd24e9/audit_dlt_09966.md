# [?] Avoid double free in simplicity pointer when copying PrecomputedTransactionData

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2025-03-03
Source: https://github.com/ElementsProject/elements/commit/3a80782963e3d7bd5b5b6acdd4236bdc75ddadbb
Type: security-commit

## Details
Avoid double free in simplicity pointer when copying PrecomputedTransactionData

We cannot put a raw pointer into a class that has a default copy constructor.

## Patch
### src/script/interpreter.cpp
```diff
@@ -2669,7 +2669,7 @@ void PrecomputedTransactionData::Init(const T& txTo, std::vector<CTxOut>&& spent
         simplicityRawTx.version = txTo.nVersion;
         simplicityRawTx.lockTime = txTo.nLockTime;
 
-        m_simplicity_tx_data = simplicity_elements_mallocTransaction(&simplicityRawTx);
+        m_simplicity_tx_data = SimplicityTransactionUniquePtr(simplicity_elements_mallocTransaction(&simplicityRawTx));
 
         m_bip341_taproot_ready = true;
     }
@@ -3121,7 +3121,7 @@ bool GenericTransactionSignatureChecker<T>::CheckSimplicity(const valtype& progr
 
     assert(txdata->m_simplicity_tx_data);
     assert(simplicityTapEnv);
-    if (!simplicity_elements_execSimplicity(&error, 0, txdata->m_simplicity_tx_data, nIn, simplicityTapEnv, txdata->m_hash_genesis_block.data(), budget, 0, program.data(), program.size(), witness.data(), witness.size())) {
+    if (!simplicity_elements_execSimplicity(&error, 0, txdata->m_simplicity_tx_data.get(), nIn, simplicityTapEnv, txdata->m_hash_genesis_block.data(), budget, 0, program.data(), program.size(), witness.data(), witness.size())) {
         assert(!"simplicity_elements_execSimplicity internal error");
     }
     simplicity_elements_freeTapEnv(simplicityTapEnv);
```

### src/script/interpreter.h
```diff
@@ -169,9 +169,18 @@ enum : uint32_t {
 
 bool CheckSignatureEncoding(const std::vector<unsigned char> &vchSig, unsigned int flags, ScriptError* serror);
 
+struct SimplicityTransactionDeleter
+{
+    void operator()(transaction* ptr)
+    {
+        simplicity_elements_freeTransaction(ptr);
+    }
+};
+using SimplicityTransactionUniquePtr = std::unique_ptr<transaction, SimplicityTransactionDeleter>;
+
 struct PrecomputedTransactionData
 {
-    transaction* m_simplicity_tx_data = nullptr;
+    SimplicityTransactionUniquePtr m_simplicity_tx_data;
     // BIP341 precomputed data.
     // These are single-SHA256, see https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki#cite_note-15.
     uint256 m_prevouts_single_hash;
@@ -221,9 +230,6 @@ struct PrecomputedTransactionData
 
     template <class T>
     explicit PrecomputedTransactionData(const T& tx);
-    ~PrecomputedTransactionData() {
-        simplicity_elements_freeTransaction(m_simplicity_tx_data);
-    }
 };
 
 enum class SigVersion
```

### src/test/fuzz/simplicity.cpp
```diff
@@ -204,13 +204,13 @@ FUZZ_TARGET_INIT(simplicity, initialize_simplicity)
     PrecomputedTransactionData txdata{GENESIS_HASH};
     std::vector<CTxOut> spent_outs_copy{spent_outs};
     txdata.Init(mtx, std::move(spent_outs_copy));
-    assert(txdata.m_simplicity_tx_data != NULL);
+    assert(txdata.m_simplicity_tx_data);
 
     // 4. Main test
     unsigned char imr_out[32];
     unsigned char *imr = mtx.vin[0].prevout.hash.data()[2] & 2 ? imr_out : NULL;
 
-    const transaction* tx = txdata.m_simplicity_tx_data;
+    const transaction* tx = txdata.m_simplicity_tx_data.get();
     tapEnv* taproot = simplicity_elements_mallocTapEnv(&simplicityRawTap);
     simplicity_elements_execSimplicity(&error, imr, tx, nIn, taproot, GENESIS_HASH.data(), budget, amr, prog_bytes.data(), prog_bytes.size(), wit_bytes.data(), wit_bytes.size());
 
```

### src/test/fuzz/simplicity_tx.cpp
```diff
@@ -217,7 +217,7 @@ FUZZ_TARGET_INIT(simplicity_tx, initialize_simplicity_tx)
         // that we will allocate Simplicity data. The check for whether to do this is very
         // lax: is this a 34-byte scriptPubKey that starts with OP_1 and does it have a
         // nonempty witness.
-        assert(txdata.m_simplicity_tx_data != NULL);
+        assert(txdata.m_simplicity_tx_data);
     }
 
     const CTransaction tx{mtx};
```
