# [?] Drop the response lock to prevent deadlock

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2023-11-09
Source: https://github.com/AleoNet/snarkOS-test/commit/a2aa93d05ea413d1aee473211f13dc97fe4d4b7f
Type: security-commit

## Details
Drop the response lock to prevent deadlock

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
