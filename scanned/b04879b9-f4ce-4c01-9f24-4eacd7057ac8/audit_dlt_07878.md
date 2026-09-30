# [?] Avoid overflow in the initial 'nextExchangeTransitionConfTime' calculation (#3809)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-06-28
Source: https://github.com/status-im/nimbus-eth2/commit/fa7d7fcc42c2c8145539a5a27235a3a38381fb70
Type: security-commit

## Details
Avoid overflow in the initial 'nextExchangeTransitionConfTime' calculation (#3809)

## Patch
### beacon_chain/nimbus_beacon_node.nim
```diff
@@ -712,11 +712,19 @@ proc init*(T: type BeaconNode,
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
-Subproject commit 2a5095505f771610f9559d2e774b2a9561f01101
+Subproject commit a5bc5ca996ab72c1c5dda7d5b922b536f39f603e
```
