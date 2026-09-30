# [?] Fix potential panics related to time (#4951)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-02-17
Source: https://github.com/paritytech/substrate/commit/6e7c5433a9927dad2d993838823000e4da0d111b
Type: security-commit

## Details
Fix potential panics related to time (#4951)

* Fix potential peerset panic at initialization

* Also fix legacy_proto/behaviour.rs

## Patch
### client/network/src/protocol/legacy_proto/behaviour.rs
```diff
@@ -379,12 +379,14 @@ impl LegacyProto {
 			}
 		};
 
+		let now = Instant::now();
+
 		match mem::replace(occ_entry.get_mut(), PeerState::Poisoned) {
-			PeerState::Banned { ref until } if *until > Instant::now() => {
+			PeerState::Banned { ref until } if *until > now => {
 				debug!(target: "sub-libp2p", "PSM => Connect({:?}): Will start to connect at \
 					until {:?}", occ_entry.key(), until);
 				*occ_entry.into_mut() = PeerState::PendingRequest {
-					timer: futures_timer::Delay::new(until.clone() - Instant::now()),
+					timer: futures_timer::Delay::new(until.clone() - now),
 					timer_deadline: until.clone(),
 				};
 			},
@@ -397,13 +399,13 @@ impl LegacyProto {
 			},
 
 			PeerState::Disabled { open, ref connected_point, banned_until: Some(ref banned) }
-				if *banned > Instant::now() => {
+				if *banned > now => {
 				debug!(target: "sub-libp2p", "PSM => Connect({:?}): Has idle connection through \
 					{:?} but node is banned until {:?}", occ_entry.key(), connected_point, banned);
 				*occ_entry.into_mut() = PeerState::DisabledPendingEnable {
 					connected_point: connected_point.clone(),
 					open,
-					timer: futures_timer::Delay::new(banned.clone() - Instant::now()),
+					timer: futures_timer::Delay::new(banned.clone() - now),
 					timer_deadline: banned.clone(),
 				};
 			},
```

### client/peerset/src/lib.rs
```diff
@@ -199,14 +199,16 @@ impl Peerset {
 			tx: tx.clone(),
 		};
 
+		let now = Instant::now();
+
 		let mut peerset = Peerset {
 			data: peersstate::PeersState::new(config.in_peers, config.out_peers, config.reserved_only),
 			tx,
 			rx,
 			reserved_only: config.reserved_only,
 			message_queue: VecDeque::new(),
-			created: Instant::now(),
-			latest_time_update: Instant::now(),
+			created: now,
+			latest_time_update: now,
 		};
 
 		peerset.data.set_priority_group(RESERVED_NODES, config.reserved_nodes.into_iter().collect());
```
