# [?] Merge pull request #2830 from AleoHQ/fix/responses-deadlock

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2023-11-10
Source: https://github.com/AleoNet/snarkOS-test/commit/8884db2c620cf8a592ab3f22cbe39095114e04a7
Type: security-commit

## Details
Merge pull request #2830 from AleoHQ/fix/responses-deadlock

Prevent deadlock in block_sync

## Patch
### node/sync/src/block_sync.rs
```diff
@@ -451,6 +451,8 @@ impl<N: Network> BlockSync<N> {
             if block != existing_block {
                 // Remove the candidate block.
                 responses.remove(&height);
+                // Drop the write lock on the responses map.
+                drop(responses);
                 // Remove all block requests to the peer.
                 self.remove_block_requests_to_peer(&peer_ip);
                 bail!("Candidate block {height} from '{peer_ip}' is malformed");
```
