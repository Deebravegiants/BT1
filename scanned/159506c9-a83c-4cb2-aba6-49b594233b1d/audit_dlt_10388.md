# [?] Avoid overflow in the initial 'nextExchangeTransitionConfTime' calculation (#3809)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-06-28
Source: https://github.com/status-im/nimbus-eth2/commit/2c3e47d7e6b184bb3dc7056fadf2a7aab9fdbede
Type: security-commit

## Details
Avoid overflow in the initial 'nextExchangeTransitionConfTime' calculation (#3809)

## Patch
### beacon_chain/nimbus_beacon_node.nim
```diff
@@ -724,11 +724,19 @@ proc init*(T: type BeaconNode,
       else:
         nil
 
-    bellatrixEpochTime =
-      genesisTime + cfg.BELLATRIX_FORK_EPOCH * SLOTS_PER_EPOCH * SECONDS_PER_SLOT
+    maxSecondsInMomentType = Moment.high.epochSeconds
+    # If the Bellatrix epoch is above this value, the calculation
+    # below will overflow. This happens in practice for networks
+    # where the `BELLATRIX_FORK_EPOCH` is not yet specified.
+    maxSupportedBellatrixEpoch = (maxSecondsInMomentType.uint64 - genesisTime) div
+                                 (SLOTS_PER_EPOCH * SECONDS_PER_SLOT)
+    bellatrixEpochTime = if cfg.BELLATRIX_FORK_EPOCH < maxSupportedBellatrixEpoch:
+      int64(genesisTime + cfg.BELLATRIX_FORK_EPOCH * SLOTS_PER_EPOCH * SECONDS_PER_SLOT)
+    else:
+      maxSecondsInMomentType
 
     nextExchangeTransitionConfTime =
-      max(Moment.init(int64 bellatrixEpochTime, Second),
+      max(Moment.init(bellatrixEpochTime, Second),
           Moment.now)
 
   let node = BeaconNode(
```

### vendor/nim-chronos
```diff
@@ -1 +1 @@
-Subproject commit c6ce4d4fb26a785aabff84793fcd2b86a0ff93af
+Subproject commit 84e32a3b695b2e54ff7733ca660bd95332b21d38
```
