# [?] Fix crash when `--in-peers` & `--out-peers` both 0 (#14598)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2023-07-20
Source: https://github.com/paritytech/substrate/commit/23da984e5c792150e346206679e7a7a6d415cfbd
Type: security-commit

## Details
Fix crash when `--in-peers` & `--out-peers` both 0 (#14598)

## Patch
### client/network/sync/src/block_request_handler.rs
```diff
@@ -153,7 +153,8 @@ where
 	) -> (Self, ProtocolConfig) {
 		// Reserve enough request slots for one request per peer when we are at the maximum
 		// number of peers.
-		let (tx, request_receiver) = async_channel::bounded(num_peer_hint);
+		let capacity = std::cmp::max(num_peer_hint, 1);
+		let (tx, request_receiver) = async_channel::bounded(capacity);
 
 		let mut protocol_config = generate_protocol_config(
 			protocol_id,
```

### client/network/sync/src/state_request_handler.rs
```diff
@@ -131,7 +131,8 @@ where
 	) -> (Self, ProtocolConfig) {
 		// Reserve enough request slots for one request per peer when we are at the maximum
 		// number of peers.
-		let (tx, request_receiver) = async_channel::bounded(num_peer_hint);
+		let capacity = std::cmp::max(num_peer_hint, 1);
+		let (tx, request_receiver) = async_channel::bounded(capacity);
 
 		let mut protocol_config = generate_protocol_config(
 			protocol_id,
```

### client/service/src/builder.rs
```diff
@@ -785,12 +785,14 @@ where
 	};
 
 	let (state_request_protocol_config, state_request_protocol_name) = {
+		let num_peer_hint = net_config.network_config.default_peers_set_num_full as usize +
+			net_config.network_config.default_peers_set.reserved_nodes.len();
 		// Allow both outgoing and incoming requests.
 		let (handler, protocol_config) = StateRequestHandler::new(
 			&protocol_id,
 			config.chain_spec.fork_id(),
 			client.clone(),
-			net_config.network_config.default_peers_set_num_full as usize,
+			num_peer_hint,
 		);
 		let config_name = protocol_config.name.clone();
 
```
