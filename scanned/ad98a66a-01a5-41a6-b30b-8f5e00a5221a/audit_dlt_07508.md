# [?] chore: Update protobuf to fix RUSTSEC-2024-0437 (#6292)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-04-24
Source: https://github.com/iotaledger/iota/commit/302188b41afb046e74abc4da035d8a5ca56b30d0
Type: security-commit

## Details
chore: Update protobuf to fix RUSTSEC-2024-0437 (#6292)

## Description 

Updates `protobuf` to version 3 (and prometheus along with it) to fix
RUSTSEC-2024-0437.

## Related Issues

Closes #5861

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

---------

Co-authored-by: Thibault Martinez <thibault@iota.org>

## Patch
### Cargo.lock
```diff
@@ -11821,17 +11821,17 @@ dependencies = [
 
 [[package]]
 name = "prometheus"
-version = "0.13.4"
+version = "0.14.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3d33c28a30771f7f96db69893f78b857f7450d7e0237e9c8fc6427a81bae7ed1"
+checksum = "3ca5326d8d0b950a9acd87e6a3f94745394f62e4dae1b1ee22b2bc0c394af43a"
 dependencies = [
  "cfg-if",
  "fnv",
  "lazy_static",
  "memchr",
  "parking_lot 0.12.3",
  "protobuf",
- "thiserror 1.0.64",
+ "thiserror 2.0.12",
 ]
 
 [[package]]
@@ -11955,11 +11955,23 @@ dependencies = [
 
 [[package]]
 name = "protobuf"
-version = "2.28.0"
+version = "3.7.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "106dd99e98437432fed6519dedecfade6a06a73bb7b2a1e019fdd2bee5778d94"
+checksum = "d65a1d4ddae7d8b5de68153b48f6aa3bba8cb002b243dbdbc55a5afbc98f99f4"
 dependencies = [
  "bytes",
+ "once_cell",
+ "protobuf-support",
+ "thiserror 1.0.64",
+]
+
+[[package]]
+name = "protobuf-support"
+version = "3.7.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "3e36c2f31e0a47f9280fb347ef5e461ffcd2c52dd520d8e216b52f93b0b0d7d6"
+dependencies = [
+ "thiserror 1.0.64",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -301,11 +301,11 @@ passkey-client = "0.4.0"
 passkey-types = "0.4.0"
 pretty_assertions = "1.3.0"
 proc-macro2 = "1.0.47"
-prometheus = "0.13.3"
+prometheus = "0.14.0"
 proptest = "1.1.0"
 proptest-derive = "0.5.1"
 prost = "0.13"
-protobuf = { version = "2.28", features = ["with-bytes"] }
+protobuf = { version = "3.7.2", features = ["with-bytes"] }
 quinn-proto = "0.11.7"
 quote = "1.0.23"
 rand = "0.8.5"
```

### consensus/core/src/ancestor.rs
```diff
@@ -204,7 +204,7 @@ impl AncestorStateManager {
                         .metrics
                         .node_metrics
                         .ancestor_state_change_by_authority
-                        .with_label_values(&[block_hostname, "exclude"])
+                        .with_label_values(&[block_hostname.as_str(), "exclude"])
                         .inc();
                 }
             }
@@ -227,7 +227,7 @@ impl AncestorStateManager {
                         .metrics
                         .node_metrics
                         .ancestor_state_change_by_authority
-                        .with_label_values(&[block_hostname, "include"])
+                        .with_label_values(&[block_hostname.as_str(), "include"])
                         .inc();
                 }
             }
```

### consensus/core/src/authority_service.rs
```diff
@@ -96,7 +96,11 @@ impl<C: CoreThreadDispatcher> NetworkService for AuthorityService<C> {
                 .metrics
                 .node_metrics
                 .invalid_blocks
-                .with_label_values(&[peer_hostname, "handle_send_block", "UnexpectedAuthority"])
+                .with_label_values(&[
+                    peer_hostname.as_str(),
+                    "handle_send_block",
+                    "UnexpectedAuthority",
+                ])
                 .inc();
             let e = ConsensusError::UnexpectedAuthority(signed_block.author(), peer);
             info!("Block with wrong authority from {}: {}", peer, e);
@@ -110,7 +114,11 @@ impl<C: CoreThreadDispatcher> NetworkService for AuthorityService<C> {
                 .metrics
                 .node_metrics
                 .invalid_blocks
-                .with_label_values(&[peer_hostname, "handle_send_block", e.clone().name()])
+                .with_label_values(&[
+                    peer_hostname.as_str(),
+                    "handle_send_block",
+                    e.clone().name(),
+                ])
                 .inc();
             info!("Invalid block from {}: {}", peer, e);
             return Err(e);
@@ -152,7 +160,7 @@ impl<C: CoreThreadDispatcher> NetworkService for AuthorityService<C> {
                 .metrics
                 .node_metrics
                 .block_timestamp_drift_wait_ms
-                .with_label_values(&[peer_hostname, "handle_send_block"])
+                .with_label_values(&[peer_hostname.as_str(), "handle_send_block"])
                 .inc_by(forward_time_drift.as_millis() as u64);
             debug!(
                 "Block {:?} timestamp ({} > {}) is in the future, waiting for {}ms",
```

### consensus/core/src/block_manager.rs
```diff
@@ -381,7 +381,7 @@ impl BlockManager {
                 .metrics
                 .node_metrics
                 .invalid_blocks
-                .with_label_values(&[&hostname, "accept_block", "InvalidAncestors"])
+                .with_label_values(&[hostname.as_str(), "accept_block", "InvalidAncestors"])
                 .inc();
             warn!("Invalid block {:?} is rejected", block);
         }
```

### consensus/core/src/commit_syncer.rs
```diff
@@ -508,7 +508,7 @@ impl<C: NetworkClient> CommitSyncer<C> {
                             .metrics
                             .node_metrics
                             .commit_sync_fetch_once_errors
-                            .with_label_values(&[&hostname, error])
+                            .with_label_values(&[hostname.as_str(), error])
                             .inc();
                     }
                     Err(_) => {
@@ -524,7 +524,7 @@ impl<C: NetworkClient> CommitSyncer<C> {
                             .metrics
                             .node_metrics
                             .commit_sync_fetch_once_errors
-                            .with_label_values(&[&hostname, "FetchTimeout"])
+                            .with_label_values(&[hostname.as_str(), "FetchTimeout"])
                             .inc();
                     }
                 }
@@ -666,7 +666,7 @@ impl<C: NetworkClient> CommitSyncer<C> {
                 .metrics
                 .node_metrics
                 .block_timestamp_drift_wait_ms
-                .with_label_values(&[peer_hostname, "commit_syncer"])
+                .with_label_values(&[peer_hostname.as_str(), "commit_syncer"])
                 .inc_by(forward_drift);
             let forward_drift = Duration::from_millis(forward_drift);
             if forward_drift >= inner.context.parameters.max_forward_time_drift {
```

### consensus/core/src/core.rs
```diff
@@ -1197,7 +1197,7 @@ impl Core {
                 ancestors_to_propose.push(ancestor);
                 node_metrics
                     .included_excluded_proposal_ancestors_count_by_authority
-                    .with_label_values(&[block_hostname, "timeout"])
+                    .with_label_values(&[block_hostname.as_str(), "timeout"])
                     .inc();
             } else {
                 excluded_ancestors.push((score, ancestor));
@@ -1289,7 +1289,7 @@ impl Core {
             );
             node_metrics
                 .included_excluded_proposal_ancestors_count_by_authority
-                .with_label_values(&[block_hostname, "quorum"])
+                .with_label_values(&[block_hostname.as_str(), "quorum"])
                 .inc();
         }
 
```

### consensus/core/src/network/metrics_layer.rs
```diff
@@ -113,7 +113,7 @@ impl MetricsResponseCallback {
     pub(crate) fn on_error<E>(self, _error: &E) {
         self.metrics
             .errors
-            .with_label_values(&[&self.route, "unknown"])
+            .with_label_values(&[self.route.as_str(), "unknown"])
             .inc();
     }
 }
```

### consensus/core/src/subscriber.rs
```diff
@@ -171,7 +171,7 @@ impl<C: NetworkClient, S: NetworkService> Subscriber<C, S> {
                         .metrics
                         .node_metrics
                         .subscriber_connection_attempts
-                        .with_label_values(&[peer_hostname, "success"])
+                        .with_label_values(&[peer_hostname.as_str(), "success"])
                         .inc();
                     blocks
                 }
@@ -184,7 +184,7 @@ impl<C: NetworkClient, S: NetworkService> Subscriber<C, S> {
                         .metrics
                         .node_metrics
                         .subscriber_connection_attempts
-                        .with_label_values(&[peer_hostname, "failure"])
+                        .with_label_values(&[peer_hostname.as_str(), "failure"])
                         .inc();
                     continue 'subscription;
                 }
```

### consensus/core/src/synchronizer.rs
```diff
@@ -574,13 +574,13 @@ impl<C: NetworkClient, V: BlockVerifier, D: CoreThreadDispatcher> Synchronizer<C
         let peer_hostname = &context.committee.authority(peer_index).hostname;
         metrics
             .synchronizer_fetched_blocks_by_peer
-            .with_label_values(&[peer_hostname, sync_method])
+            .with_label_values(&[peer_hostname.as_str(), sync_method])
             .inc_by(blocks.len() as u64);
         for block in &blocks {
             let block_hostname = &context.committee.authority(block.author()).hostname;
             metrics
                 .synchronizer_fetched_blocks_by_authority
-                .with_label_values(&[block_hostname, sync_method])
+                .with_label_values(&[block_hostname.as_str(), sync_method])
                 .inc();
         }
 
@@ -657,7 +657,7 @@ impl<C: NetworkClient, V: BlockVerifier, D: CoreThreadDispatcher> Synchronizer<C
                     .metrics
                     .node_metrics
                     .invalid_blocks
-                    .with_label_values(&[&hostname, "synchronizer", e.clone().name()])
+                    .with_label_values(&[hostname.as_str(), "synchronizer", e.clone().name()])
                     .inc();
                 warn!("Invalid block received from {}: {}", peer_index, e);
                 return Err(e);
@@ -769,7 +769,7 @@ impl<C: NetworkClient, V: BlockVerifier, D: CoreThreadDispatcher> Synchronizer<C
                                                 .metrics
                                                 .node_metrics
                                                 .invalid_blocks
-                                                .with_label_values(&[&hostname, "synchronizer_own_block", err.clone().name()])
+                                                .with_label_values(&[hostname.as_str(), "synchronizer_own_block", err.clone().name()])
                                                 .inc();
                                             warn!("Invalid block received from {}: {}", authority_index, err);
                                         })?;
```

### crates/iota-benchmark/src/lib.rs
```diff
@@ -456,7 +456,7 @@ impl ValidatorProxy for LocalValidatorAggregatorProxy {
                         .load()
                         .metrics
                         .process_tx_errors
-                        .with_label_values(&[&name.concise().to_string(), e.as_ref()])
+                        .with_label_values(&[name.concise().to_string().as_str(), e.as_ref()])
                         .inc();
                     tracing::warn!("Failed to submit transaction: {e}")
                 }
@@ -559,7 +559,7 @@ impl ValidatorProxy for LocalValidatorAggregatorProxy {
                     auth_agg
                         .metrics
                         .process_cert_errors
-                        .with_label_values(&[&name.concise().to_string(), e.as_ref()])
+                        .with_label_values(&[name.concise().to_string().as_str(), e.as_ref()])
                         .inc();
                     tracing::warn!("Failed to submit certificate: {e}")
                 }
```

### crates/iota-core/src/authority_aggregator.rs
```diff
@@ -1125,7 +1125,7 @@ where
                                 debug!(?tx_digest, name=?concise_name, weight, "Error processing transaction from validator: {:?}", err);
                                 self.metrics
                                     .process_tx_errors
-                                    .with_label_values(&[&display_name, err.as_ref()])
+                                    .with_label_values(&[display_name.as_str(), err.as_ref()])
                                     .inc();
                                 Self::record_rpc_error_maybe(self.metrics.clone(), &display_name, &err);
                                 let (retryable, categorized) = err.is_retryable();
@@ -1660,7 +1660,7 @@ where
                             debug!(?tx_digest, name=?concise_name, "Error processing certificate from validator: {:?}", err);
                             metrics
                                 .process_cert_errors
-                                .with_label_values(&[&display_name, err.as_ref()])
+                                .with_label_values(&[display_name.as_str(), err.as_ref()])
                                 .inc();
                             Self::record_rpc_error_maybe(metrics, &display_name, &err);
                             let (retryable, categorized) = err.is_retryable();
```
