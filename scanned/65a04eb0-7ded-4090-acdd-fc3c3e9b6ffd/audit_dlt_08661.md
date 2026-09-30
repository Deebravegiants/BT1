# [?] fix: properly fix a deadlock in PeerPoolHandling::insert_candidate_peers

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2025-10-09
Source: https://github.com/AleoNet/snarkOS-test/commit/078e5cd3b47dea11966f18fb50ff4c4136cb7458
Type: security-commit

## Details
fix: properly fix a deadlock in PeerPoolHandling::insert_candidate_peers

Signed-off-by: ljedrz <ljedrz@users.noreply.github.com>

## Patch
### node/router/src/lib.rs
```diff
@@ -217,8 +217,7 @@ pub trait PeerPoolHandling<N: Network>: P2P {
     fn insert_candidate_peers(&self, mut listener_addrs: Vec<(SocketAddr, Option<u32>)>) {
         // Hold a write guard from now on, so as not to accidentally slash multiple times
         // based on multiple batches of candidate peers, and to not overwrite any entries.
-        // Reject multiple overlapping entries via `RwLock::try_write`.
-        let Some(mut peer_pool) = self.peer_pool().try_write() else { return };
+        let mut peer_pool = self.peer_pool().write();
 
         // Perform filtering to ensure candidate validity. Also count how many entries are updates.
         let mut num_updates: usize = 0;
@@ -242,7 +241,7 @@ pub trait PeerPoolHandling<N: Network>: P2P {
         }
 
         // If we're about to exceed the peer pool size limit, apply candidate slashing.
-        if self.number_of_peers() + listener_addrs.len() - num_updates >= Self::MAXIMUM_POOL_SIZE
+        if peer_pool.len() + listener_addrs.len() - num_updates >= Self::MAXIMUM_POOL_SIZE
             && Self::PEER_SLASHING_COUNT != 0
         {
             // Collect the addresses of prospect peers.
@@ -272,7 +271,7 @@ pub trait PeerPoolHandling<N: Network>: P2P {
         }
 
         // Make sure that we won't breach the pool size limit in case the slashing didn't suffice.
-        listener_addrs.truncate(Self::MAXIMUM_POOL_SIZE.saturating_sub(self.number_of_peers()));
+        listener_addrs.truncate(Self::MAXIMUM_POOL_SIZE.saturating_sub(peer_pool.len()));
 
         // If we've managed to truncate to 0, exit.
         if listener_addrs.is_empty() {
```
