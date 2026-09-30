# [?] fixed underflow issue

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-11-28
Source: https://github.com/Zilliqa/zq1/commit/d3c54b25e559cc1467e9e1fc62763318c6de6a7d
Type: security-commit

## Details
fixed underflow issue

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -57,7 +57,7 @@
 using namespace std;
 using namespace boost::multiprecision;
 
-const uint32_t MAX_FETCH_BLOCK_RETRIES = 5;
+const int32_t MAX_FETCH_BLOCK_RETRIES = 5;
 
 Lookup::Lookup(Mediator& mediator, SyncType syncType) : m_mediator(mediator) {
   m_syncType.store(SyncType::NO_SYNC);
@@ -1496,7 +1496,7 @@ bool Lookup::ProcessGetMicroBlockFromLookup(
     LOG_GENERAL(INFO, "[SendMB]"
                           << "Request for microBlockHash " << mbhash);
     shared_ptr<MicroBlock> mbptr;
-    int retryCount = 5;
+    int retryCount = MAX_FETCH_BLOCK_RETRIES;
 
     while (retryCount-- > 0) {
       if (!BlockStorage::GetBlockStorage().GetMicroBlock(mbhash, mbptr)) {
@@ -1654,7 +1654,7 @@ bool Lookup::ProcessGetCosigsRewardsFromSeed(
   vector<MicroBlock> retMicroBlocks;
 
   TxBlockSharedPtr txblkPtr;
-  uint32_t retryCount = MAX_FETCH_BLOCK_RETRIES;
+  int retryCount = MAX_FETCH_BLOCK_RETRIES;
   while (retryCount-- > 0) {
     if (!BlockStorage::GetBlockStorage().GetTxBlock(blockNum, txblkPtr)) {
       LOG_GENERAL(WARNING,
```
