# [?] fixed panic on empty remote read request (#4619)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-01-14
Source: https://github.com/paritytech/substrate/commit/45995b4b7d0f995e51e6c04dac20f0effba2f65e
Type: security-commit

## Details
fixed panic on empty remote read request (#4619)

## Patch
### client/network/src/protocol.rs
```diff
@@ -1472,6 +1472,13 @@ impl<B: BlockT, S: NetworkSpecialization<B>, H: ExHashT> Protocol<B, S, H> {
 		who: PeerId,
 		request: message::RemoteReadRequest<B::Hash>,
 	) {
+		if request.keys.is_empty() {
+			debug!(target: "sync", "Invalid remote read request sent by {}", who);
+			self.behaviour.disconnect_peer(&who);
+			self.peerset_handle.report_peer(who, rep::BAD_MESSAGE);
+			return;
+		}
+
 		let keys_str = || match request.keys.len() {
 			1 => request.keys[0].to_hex::<String>(),
 			_ => format!(
@@ -1510,6 +1517,13 @@ impl<B: BlockT, S: NetworkSpecialization<B>, H: ExHashT> Protocol<B, S, H> {
 		who: PeerId,
 		request: message::RemoteReadChildRequest<B::Hash>,
 	) {
+		if request.keys.is_empty() {
+			debug!(target: "sync", "Invalid remote child read request sent by {}", who);
+			self.behaviour.disconnect_peer(&who);
+			self.peerset_handle.report_peer(who, rep::BAD_MESSAGE);
+			return;
+		}
+
 		let keys_str = || match request.keys.len() {
 			1 => request.keys[0].to_hex::<String>(),
 			_ => format!(
```

### client/rpc/src/state/state_light.rs
```diff
@@ -325,8 +325,8 @@ impl<Block, F, B, E, RA> StateBackend<B, E, Block, RA> for LightState<Block, F,
 		keys: Option<Vec<StorageKey>>
 	) {
 		let keys = match keys {
-			Some(keys) => keys,
-			None => {
+			Some(keys) if !keys.is_empty() => keys,
+			_ => {
 				warn!("Cannot subscribe to all keys on light client. Subscription rejected.");
 				return;
 			}
```
