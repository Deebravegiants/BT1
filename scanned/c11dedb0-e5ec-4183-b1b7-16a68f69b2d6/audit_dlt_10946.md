# [?] Fix potential software crash when using 'at' to access key doesn't exist

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-10-26
Source: https://github.com/Zilliqa/zq1/commit/e227b6c7d5d97026f8bad05845a585a2e4d80512
Type: security-commit

## Details
Fix potential software crash when using 'at' to access key doesn't exist

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -2946,7 +2946,7 @@ void Lookup::SendTxnPacketToNodes(uint32_t numShards) {
 
       result = Messenger::SetNodeForwardTxnBlock(
           msg, MessageOffset::BODY, m_mediator.m_currentEpochNum, i,
-          m_mediator.m_selfKey, m_txnShardMap[i], mp.at(i));
+          m_mediator.m_selfKey, m_txnShardMap[i], mp[i]);
     }
 
     if (!result) {
```
