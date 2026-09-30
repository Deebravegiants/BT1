# [?] Fix race condition in the syncing sim (#944)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-03-23
Source: https://github.com/sigp/lighthouse/commit/f8bc045a01764f81c32f48c496cabee8281f965e
Type: security-commit

## Details
Fix race condition in the syncing sim (#944)

* Fix race condition in the syncing sim

* Update another strategy

## Patch
### tests/simulator/src/local_network.rs
```diff
@@ -94,7 +94,7 @@ impl<E: EthSpec> LocalNetwork<E> {
                         .expect("bootnode must have a network"),
                 );
             })
-            .expect("should have atleast one node");
+            .expect("should have at least one node");
 
         let index = self.beacon_nodes.read().len();
 
```

### tests/simulator/src/sync_sim.rs
```diff
@@ -94,8 +94,10 @@ pub fn verify_two_nodes_sync<E: EthSpec>(
         // Add beacon nodes
         network
             .add_beacon_node(beacon_config.clone())
-            .join(network.add_beacon_node(beacon_config.clone()))
-            .map(|_| network)
+            .map(|_| (network, beacon_config))
+            .and_then(|(network, beacon_config)| {
+                network.add_beacon_node(beacon_config).map(|_| network)
+            })
     })
     .and_then(move |network| {
         // Delay for `sync_delay` epochs before verifying synced state.
@@ -128,8 +130,10 @@ pub fn verify_in_between_sync<E: EthSpec>(
         // Add a beacon node
         network
             .add_beacon_node(beacon_config.clone())
-            .join(network.add_beacon_node(beacon_config.clone()))
-            .map(|_| network)
+            .map(|_| (network, beacon_config))
+            .and_then(|(network, beacon_config)| {
+                network.add_beacon_node(beacon_config).map(|_| network)
+            })
     })
     .and_then(move |network| {
         // Delay before adding additional syncing nodes.
```
