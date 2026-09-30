# [?] Merge #18433: serialization: prevent int overflow for big Coin::nHeight

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-03-30
Source: https://github.com/litecoin-project/litecoin/commit/6a11d9e33034242cbb3398f7eb4b448d034072c7
Type: security-commit

## Details
Merge #18433: serialization: prevent int overflow for big Coin::nHeight

e980214bc4fd49530e8d50fe0a6657b8583bc6b5 serialization: prevent int overflow for big Coin::nHeight (pierrenn)

Pull request description:

  This is an attempt to fix fuzzer issues 1,2,8 reported by practicalswift here : https://github.com/bitcoin/bitcoin/issues/18046

  The fuzzer harness doesn't prevent deserialization of unrealistic high values for `Coin::nHeight`.  In the [provided examples](https://github.com/bitcoin/bitcoin/issues/18046), we have :
  - `blockundo_deserialize` : the varint `0x8DD88DD700` is deserialized as `3944983552` in `Coin::nHeight` (`TxInOutFormatter::Unser`)
  - `coins_deserialize` : the varint `0x8DD5D5EC40` is deserialized as `3939874496` similarly
  - `txundo_deserialize`: the varint `0x8DCD828F01` is deserialized as `3921725441` in `Coin::nHeight` (`Coin::Unserialize`)

  Since `Coin::nHeight` is 31 bit long, multiplying a large value by 2 triggers the fuzzer.

  AFAIK those values are unrealistic (~70k years for the smallest..). I've looked a bit a reducing the range of values the fuzzer can deserialize, but this seems to be too much code change for not much.

  Hence this PR chooses to static cast `nHeight` when re-serializing; it seems to be the less intrusive/safest way to prevent the fuzzer output.

  Another more "upstream" approach would be to limit `Coin::nHeight` values to something more realistic, e.g. `0xFFFFFFF` (~5k years) :

  https://github.com/pierreN/bitcoin/blob/de3a30bab28e2db853a795017c5ec1704a1d0fee/src/undo.h#L39 and https://github.com/pierreN/bitcoin/blob/de3a30bab28e2db853a795017c5ec1704a1d0fee/src/coins.h#L71

  Thanks !

  NB: i was also not sure about the component/area to prefix the PR/commit with.. ?

ACKs for top commit:
  practicalswift:
    ACK e980214bc4fd49530e8d50fe0a6657b8583bc6b5 -- patch looks correct
  promag:
    ACK e980214bc4fd49530e8d50fe0a6657b8583bc6b5.
  sipa:
    utACK e980214bc4fd49530e8d50fe0a6657b8583bc6b5
  MarcoFalke:
    re-ACK e980214bc4fd49530e8d50fe0a6657b8583bc6b5 🎑
  ryanofsky:
    Code review ACK e980214bc4fd49530e8d50fe0a6657b8583bc6b5. Just removed ternary ? 1 : 0 and replaced / 2 with >> 1 since last review

Tree-SHA512: 905fc9e5e52a6857abee4a1c863751767835965804bb8c39474f27a120f65399ff4ba7a49ef1da0ba565379f8c12095bd384b6c492cf06776f01b2db68d522b8

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
