# [?] Protect against timing underflows (#1111)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-05-06
Source: https://github.com/sigp/lighthouse/commit/4afcf721b9c0f5603e85f480fcba4bcbcb95e743
Type: security-commit

## Details
Protect against timing underflows (#1111)

## Patch
### beacon_node/eth2-libp2p/src/peer_manager/mod.rs
```diff
@@ -392,8 +392,17 @@ impl<TSpec: EthSpec> PeerManager<TSpec> {
                     // For disconnected peers, lower their reputation by 1 for every hour they
                     // stay disconnected. This helps us slowly forget disconnected peers.
                     // In the same way, slowly allow banned peers back again.
-                    let dc_hours = (now - since).as_secs() / 3600;
-                    let last_dc_hours = (self.last_updated - since).as_secs() / 3600;
+                    let dc_hours = now
+                        .checked_duration_since(since)
+                        .unwrap_or_else(|| Duration::from_secs(0))
+                        .as_secs()
+                        / 3600;
+                    let last_dc_hours = self
+                        .last_updated
+                        .checked_duration_since(since)
+                        .unwrap_or_else(|| Duration::from_secs(0))
+                        .as_secs()
+                        / 3600;
                     if dc_hours > last_dc_hours {
                         // this should be 1 most of the time
                         let rep_dif = (dc_hours - last_dc_hours)
```
