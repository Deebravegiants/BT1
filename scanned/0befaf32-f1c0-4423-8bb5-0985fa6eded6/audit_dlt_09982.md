# [?] tests: Clarify how we avoid hitting the signed integer overflow in CFeeRate::GetFeePerK() when fuzzing

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-04-30
Source: https://github.com/litecoin-project/litecoin/commit/2bcc2bd742392730b4f21e3d4f00438c34acac1f
Type: security-commit

## Details
tests: Clarify how we avoid hitting the signed integer overflow in CFeeRate::GetFeePerK() when fuzzing

## Patch
### src/test/fuzz/util.h
```diff
@@ -104,7 +104,10 @@ NODISCARD inline CTxMemPoolEntry ConsumeTxMemPoolEntry(FuzzedDataProvider& fuzze
 {
     // Avoid:
     // policy/feerate.cpp:28:34: runtime error: signed integer overflow: 34873208148477500 * 1000 cannot be represented in type 'long'
-    const CAmount fee = ConsumeMoney(fuzzed_data_provider) / static_cast<CAmount>(100);
+    //
+    // Reproduce using CFeeRate(348732081484775, 10).GetFeePerK()
+    const CAmount fee = std::min<CAmount>(ConsumeMoney(fuzzed_data_provider), std::numeric_limits<CAmount>::max() / static_cast<CAmount>(100000));
+    assert(MoneyRange(fee));
     const int64_t time = fuzzed_data_provider.ConsumeIntegral<int64_t>();
     const unsigned int entry_height = fuzzed_data_provider.ConsumeIntegral<unsigned int>();
     const bool spends_coinbase = fuzzed_data_provider.ConsumeBool();
```
