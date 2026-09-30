# [?] Hotfix: Fix a race condition leading to a busy loop preventing progress in Eth1 syncing

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-02-15
Source: https://github.com/status-im/nimbus-eth2/commit/c672628be8c9b87ef64c85d7bb50596fd378d607
Type: security-commit

## Details
Hotfix: Fix a race condition leading to a busy loop preventing progress in Eth1 syncing

## Patch
### beacon_chain/eth1/eth1_monitor.nim
```diff
@@ -947,19 +947,17 @@ proc detectPrimaryProviderComingOnline(m: Eth1Monitor) {.async.} =
       continue
 
     var tempProvider = tempProviderRes.get
-    var testRequest = tempProvider.web3.provider.net_version()
+    let testRequest = tempProvider.web3.provider.net_version()
 
-    yield testRequest
+    yield testRequest or sleepAsync(web3Timeouts)
 
-    try: await tempProvider.close()
-    except CatchableError as err:
-      debug "Failed to close temp web3 provider", err = err.msg
+    traceAsyncErrors tempProvider.close()
 
-    if testRequest.failed:
-      await sleepAsync(checkInterval)
-    elif m.state == Started:
+    if testRequest.completed and m.state == Started:
       m.state = ReadyToRestartToPrimary
       return
+    else:
+      await sleepAsync(checkInterval)
 
 proc doStop(m: Eth1Monitor) {.async.} =
   safeCancel m.runFut
@@ -1173,25 +1171,27 @@ func init(T: type FullBlockId, blk: Eth1BlockHeader|BlockObject): T =
   FullBlockId(number: Eth1BlockNumber blk.number, hash: blk.hash)
 
 proc startEth1Syncing(m: Eth1Monitor, delayBeforeStart: Duration) {.async.} =
-  if m.state in {Started, ReadyToRestartToPrimary}:
+  if m.state == Started:
     return
 
   let isFirstRun = m.state == Initialized
+  let needsReset = m.state in {Failed, ReadyToRestartToPrimary}
+
+  m.state = Started
 
   if delayBeforeStart != ZeroDuration:
     await sleepAsync(delayBeforeStart)
 
   # If the monitor died with an exception, the web3 provider may be in
   # an arbitary state, so we better reset it (not doing this has resulted
   # in resource leaks historically).
-  if not m.dataProvider.isNil and m.state == Failed:
+  if not m.dataProvider.isNil and needsReset:
     # We introduce a local var to eliminate the risk of scheduling two
     # competing calls to `close` below.
     let provider = m.dataProvider
     m.dataProvider = nil
     await provider.close()
 
-  m.state = Started
   await m.ensureDataProvider()
 
   # We might need to reset the chain if the new provider disagrees
```
