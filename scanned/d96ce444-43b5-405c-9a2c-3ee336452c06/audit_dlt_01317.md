# [?] [simulator] Fix race condition when creating LocalBeaconNode (#2137)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2021-01-14
Source: https://github.com/sigp/lighthouse/commit/e5b1a37110b72db03d5eea98a7c317b491157941
Type: security-commit

## Details
[simulator] Fix race condition when creating LocalBeaconNode (#2137)

## Issue Addressed

We have a race condition when counting the number of beacon nodes. The user could end up seeing a duplicated service name (node_N).

## Proposed Changes

I have updated to acquire write lock before counting the number of beacon nodes.

## Patch
### testing/simulator/src/local_network.rs
```diff
@@ -101,14 +101,15 @@ impl<E: EthSpec> LocalNetwork<E> {
             beacon_config.network.enr_tcp_port = Some(BOOTNODE_PORT + count);
         }
 
-        let index = self.beacon_nodes.read().len();
+        let mut write_lock = self_1.beacon_nodes.write();
+        let index = write_lock.len();
 
         let beacon_node = LocalBeaconNode::production(
             self.context.service_context(format!("node_{}", index)),
             beacon_config,
         )
         .await?;
-        self_1.beacon_nodes.write().push(beacon_node);
+        write_lock.push(beacon_node);
         Ok(())
     }
 
```
