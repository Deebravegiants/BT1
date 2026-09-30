# [?] [PoW] fix invalid signature for REMOTE_MINE

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-03-04
Source: https://github.com/Zilliqa/zq1/commit/f380a935585479098a569abb734f7949b950407c
Type: security-commit

## Details
[PoW] fix invalid signature for REMOTE_MINE

## Patch
### src/libPOW/pow.cpp
```diff
@@ -378,8 +378,7 @@ bool POW::SendWorkToProxy(const PairOfKey& pairOfKey, uint64_t blockNum,
           timeWindow);
   jsonValue[4] = "0x" + strPoWTime;
   auto powTimeBytes =
-      DataConversion::IntegerToBytes<uint32_t, sizeof(uint32_t)>(
-          POW_WINDOW_IN_SECONDS);
+      DataConversion::IntegerToBytes<uint32_t, sizeof(uint32_t)>(timeWindow);
   tmp.insert(tmp.end(), powTimeBytes.begin(), powTimeBytes.end());
 
   if (tmp.size() != (PUB_KEY_SIZE + BLOCK_HASH_SIZE + sizeof(uint64_t) +
```
