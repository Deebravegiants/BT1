# [?] serialization: prevent int overflow for big Coin::nHeight

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-03-25
Source: https://github.com/litecoin-project/litecoin/commit/e980214bc4fd49530e8d50fe0a6657b8583bc6b5
Type: security-commit

## Details
serialization: prevent int overflow for big Coin::nHeight

## Patch
### src/coins.h
```diff
@@ -59,7 +59,7 @@ class Coin
     template<typename Stream>
     void Serialize(Stream &s) const {
         assert(!IsSpent());
-        uint32_t code = nHeight * 2 + fCoinBase;
+        uint32_t code = nHeight * uint32_t{2} + fCoinBase;
         ::Serialize(s, VARINT(code));
         ::Serialize(s, Using<TxOutCompression>(out));
     }
```

### src/undo.h
```diff
@@ -24,7 +24,7 @@ struct TxInUndoFormatter
 {
     template<typename Stream>
     void Ser(Stream &s, const Coin& txout) {
-        ::Serialize(s, VARINT(txout.nHeight * 2 + (txout.fCoinBase ? 1u : 0u)));
+        ::Serialize(s, VARINT(txout.nHeight * uint32_t{2} + txout.fCoinBase ));
         if (txout.nHeight > 0) {
             // Required to maintain compatibility with older undo format.
             ::Serialize(s, (unsigned char)0);
@@ -34,9 +34,9 @@ struct TxInUndoFormatter
 
     template<typename Stream>
     void Unser(Stream &s, Coin& txout) {
-        unsigned int nCode = 0;
+        uint32_t nCode = 0;
         ::Unserialize(s, VARINT(nCode));
-        txout.nHeight = nCode / 2;
+        txout.nHeight = nCode >> 1;
         txout.fCoinBase = nCode & 1;
         if (txout.nHeight > 0) {
             // Old versions stored the version number for the last spend of
```
