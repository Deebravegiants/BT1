# [?] [antithesis] gate the double-spend deferral reachability assertion on its flag (#27986)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-09-15
Source: https://github.com/MystenLabs/sui/commit/b4ee3980260c48a25f174427aa8e206b588faa5c
Type: security-commit

## Details
[antithesis] gate the double-spend deferral reachability assertion on its flag (#27986)

## Description

Follow-up to #27971, now merged.

`defer_owned_object_double_spend` is on for devnet only at v137, so
`"Successfully deferred transaction attempting to double spend owned
object."` is reported as never reached in every `-p mainnet` / `-p
testnet` antithesis run. The site sits directly inside `if
protocol_config.defer_owned_object_double_spend()`, which is the only
use of that accessor, so the predicate is the guard verbatim.

This is the last one: diffing the v137 per-chain protocol config
snapshots, the flags that still differ between Unknown and prod are
`zklogin_circuit_mode`, the VDF/group-ops/ristretto natives,
`create_forwarding_address_registry`, `defer_owned_object_double_spend`,
and `check_object_funds_withdraw_in_execution` (handled in #27971). None
of the others has a reachability assertion behind it. After this,
anything still never-reached in a prod-config run is a genuine
workload-coverage gap rather than a gating artefact.

## Test plan

Covered by the existing consensus handler tests; the mechanism is tested
in #27971.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01FUZyH859hbNH4WshxMZFRK

---

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
- [ ] Indexing Framework:

## Patch
### crates/sui-core/src/consensus_handler.rs
```diff
@@ -27,7 +27,9 @@ use parking_lot::RwLockWriteGuard;
 use serde::{Deserialize, Serialize};
 use sui_config::node::CongestionLogConfig;
 use sui_macros::{fail_point, fail_point_arg, fail_point_if};
-use sui_protocol_config::{Chain, PerObjectCongestionControlMode, ProtocolConfig};
+use sui_protocol_config::{
+    Chain, PerObjectCongestionControlMode, ProtocolConfig, assert_reachable_gated,
+};
 use sui_types::{
     authenticator_state::ActiveJwk,
     base_types::{
@@ -1871,8 +1873,9 @@ impl<C: CheckpointServiceNotify + Send + Sync> ConsensusHandler<C> {
                         conflict_info.gas_object_conflicts,
                         conflict_info.non_gas_object_conflicts,
                     );
-                    assert_reachable!(
-                        "Successfully deferred transaction attempting to double spend owned object."
+                    assert_reachable_gated!(
+                        "Successfully deferred transaction attempting to double spend owned object.",
+                        |pc| pc.defer_owned_object_double_spend()
                     );
                     deferred_txns
                         .entry(deferral_key)
```
