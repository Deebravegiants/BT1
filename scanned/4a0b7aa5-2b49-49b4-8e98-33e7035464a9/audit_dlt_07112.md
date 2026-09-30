# [?] fix crash when attaching to syncing EL (#5695)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2024-01-08
Source: https://github.com/status-im/nimbus-eth2/commit/3c9d17a9d25f877bb0c35f665951d108bba40eaf
Type: security-commit

## Details
fix crash when attaching to syncing EL (#5695)

In #5664, `nim-json-rpc` dependency got bumped which included a change
in behaviour when processing `null` data for heap allocated objects.

- https://github.com/status-im/nim-json-rpc/pull/176

Old behaviour was to raise an exception, while new behaviour is to set
the value to `nil` but treat it as a successful parse. Old exceptions
were similar to "Parameter [result] expected JObject but got JNull".

As part of the `nim-json-rpc` bump in #5664, `el_manager.nim` was not
updated to match the new behaviour, leading to crash whenever its logic
assumes that a successfully parsed web3 `BlockObject` (heap allocated)
may be assumed to be non-`nil`.

As a quick remedy, the `el_manager.nim` is updated to transform `nil`
responses for `BlockObject` into `ValueError`, allowing reuse of the
existing and tested exception based processing.

## Patch
### beacon_chain/el/el_manager.nim
```diff
@@ -390,6 +390,11 @@ template trackedRequestWithTimeout[T](connection: ELConnection,
   awaitWithTimeout(request, deadline):
     raise newException(DataProviderTimeout, "Timeout")
 
+func raiseIfNil(web3block: BlockObject): BlockObject {.raises: [ValueError].} =
+  if web3block == nil:
+    raise newException(ValueError, "EL returned 'null' result for block")
+  web3block
+
 template cfg(m: ELManager): auto =
   m.eth1Chain.cfg
 
@@ -983,7 +988,7 @@ proc waitELToSyncDeposits(connection: ELConnection,
 
   while true:
     try:
-      discard connection.trackedRequestWithTimeout(
+      discard raiseIfNil connection.trackedRequestWithTimeout(
         "getBlockByHash",
         rpcClient.getBlockByHash(minimalRequiredBlock),
         web3RequestsTimeout,
@@ -1448,7 +1453,7 @@ proc fetchTimestamp(connection: ELConnection,
                     blk: Eth1Block) {.async.} =
   debug "Fetching block timestamp", blockNum = blk.number
 
-  let web3block = connection.trackedRequestWithTimeout(
+  let web3block = raiseIfNil connection.trackedRequestWithTimeout(
     "getBlockByHash",
     rpcClient.getBlockByHash(blk.hash.asBlockHash),
     web3RequestsTimeout)
@@ -1959,14 +1964,14 @@ proc syncBlockRange(m: ELManager,
         let lastBlock = m.eth1Chain.blocks.peekLast
         for n in max(lastBlock.number + 1, fullSyncFromBlock) ..< blk.number:
           debug "Obtaining block without deposits", blockNum = n
-          let blockWithoutDeposits = connection.trackedRequestWithTimeout(
+          let noDepositsBlock = raiseIfNil connection.trackedRequestWithTimeout(
             "getBlockByNumber",
             rpcClient.getBlockByNumber(n),
             web3RequestsTimeout)
 
           m.eth1Chain.addBlock(
-            lastBlock.makeSuccessorWithoutDeposits(blockWithoutDeposits))
-          eth1_synced_head.set blockWithoutDeposits.number.toGaugeValue
+            lastBlock.makeSuccessorWithoutDeposits(noDepositsBlock))
+          eth1_synced_head.set noDepositsBlock.number.toGaugeValue
 
       m.eth1Chain.addBlock blk
       eth1_synced_head.set blk.number.toGaugeValue
@@ -2059,12 +2064,12 @@ proc syncEth1Chain(m: ELManager, connection: ELConnection) {.async.} =
     let needsReset = m.eth1Chain.hasConsensusViolation or (block:
       let
         lastKnownBlock = m.eth1Chain.blocks.peekLast
-        matchingBlockAtNewProvider = connection.trackedRequestWithTimeout(
+        matchingBlockAtNewEl = raiseIfNil connection.trackedRequestWithTimeout(
           "getBlockByNumber",
           rpcClient.getBlockByNumber(lastKnownBlock.number),
           web3RequestsTimeout)
 
-      lastKnownBlock.hash.asBlockHash != matchingBlockAtNewProvider.hash)
+      lastKnownBlock.hash.asBlockHash != matchingBlockAtNewEl.hash)
 
     if needsReset:
       trace "Resetting the Eth1 chain",
@@ -2075,11 +2080,10 @@ proc syncEth1Chain(m: ELManager, connection: ELConnection) {.async.} =
   if shouldProcessDeposits:
     if m.eth1Chain.blocks.len == 0:
       let finalizedBlockHash = m.eth1Chain.finalizedBlockHash.asBlockHash
-      let startBlock =
-        connection.trackedRequestWithTimeout(
-          "getBlockByHash",
-          rpcClient.getBlockByHash(finalizedBlockHash),
-          web3RequestsTimeout)
+      let startBlock = raiseIfNil connection.trackedRequestWithTimeout(
+        "getBlockByHash",
+        rpcClient.getBlockByHash(finalizedBlockHash),
+        web3RequestsTimeout)
 
       m.eth1Chain.addBlock Eth1Block(
         hash: m.eth1Chain.finalizedBlockHash,
@@ -2106,7 +2110,7 @@ proc syncEth1Chain(m: ELManager, connection: ELConnection) {.async.} =
       raise newException(CorruptDataProvider, "Eth1 chain contradicts Eth2 consensus")
 
     let latestBlock = try:
-      connection.trackedRequestWithTimeout(
+      raiseIfNil connection.trackedRequestWithTimeout(
         "getBlockByNumber",
         rpcClient.eth_getBlockByNumber(blockId("latest"), false),
         web3RequestsTimeout)
@@ -2205,6 +2209,8 @@ proc testWeb3Provider*(web3Url: Uri,
     var res: typeof(read action)
     try:
       res = awaitOrRaiseOnTimeout(action, web3RequestsTimeout)
+      when res is BlockObject:
+        res = raiseIfNil res
       stdout.write "\r" & actionDesc & ": " & $res
     except CatchableError as err:
       stdout.write "\r" & actionDesc & ": Error(" & err.msg & ")"
```
