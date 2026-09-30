# [?] Avoid a possible nil dereference

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-02-04
Source: https://github.com/status-im/nimbus-eth2/commit/e0df027c1164fa44c7c0555112e0524ab6449ca9
Type: security-commit

## Details
Avoid a possible nil dereference

## Patch
### beacon_chain/eth1_monitor.nim
```diff
@@ -798,7 +798,9 @@ proc resetState(m: Eth1Monitor) {.async.} =
   m.eth1Chain.clear()
   m.latestEth1BlockNumber = 0
 
-  await m.dataProvider.close()
+  if m.dataProvider != nil:
+    await m.dataProvider.close()
+    m.dataProvider = nil
 
 proc stop*(m: Eth1Monitor) {.async.} =
   if m.state == Started:
@@ -819,7 +821,7 @@ proc syncBlockRange(m: Eth1Monitor,
                     merkleizer: ref DepositsMerkleizer,
                     fromBlock, toBlock,
                     fullSyncFromBlock: Eth1BlockNumber) {.gcsafe, async.} =
-  doAssert m.eth1Chain.blocks.len > 0
+  doAssert m.eth1Chain.blocks.len > 0 and m.dataProvider != nil
 
   var currentBlock = fromBlock
   while currentBlock <= toBlock:
```
