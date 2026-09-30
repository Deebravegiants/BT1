# [?] security: land the coordinated security patch set on master (#8997)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-13
Source: https://github.com/fedimint/fedimint/commit/85e47fe4f6f77896e3e06ed0ca1701d646b8e9ab
Type: security-commit

## Details
security: land the coordinated security patch set on master (#8997)

## Summary

This lands the coordinated security patch set on `master`: 30 commits
hardening the Lightning (LNv1/LNv2), wallet, gateway and server modules
against unauthenticated or unvalidated inputs that could crash a
guardian, corrupt consensus, or let a peer claim funds it does not own.
Each commit is self-contained, carries its own rationale in the commit
message, and is rebased onto the current `master` tip.

## Disclosure status

All known federations have been contacted and are already updated, so
these fixes are being landed in the open.

## Details

The patches fall into a few groups:

**Contract funding and claiming (LNv1/LNv2).** Incoming contracts could
be funded more than once, funded with a ciphertext that no offer commits
to, or funded with a caller-chosen decryption outcome. The last of these
is the most damaging: the resulting decryption-share key is never
consumed, so every guardian re-emits a consensus item for it once per
second for the life of the federation, and nothing short of a migration
removes it. The fixes reject duplicate funding, bind the ciphertext to
its offer, and require a pending decryption at funding time.

**Consensus version gating.** Three of the new rules cannot be applied
unconditionally: pre-existing sessions accepted the inputs they now
reject and must replay identically, and an ungated rejection would split
upgraded from un-upgraded peers on an ordered item mid-upgrade. LNv1
therefore gains the consensus-version voting mechanism already used by
walletv1, and the new rules activate at LN consensus version 2.1/2.3 and
wallet 2.3.

**Panic containment.** Several API and consensus paths could be driven
into a panic by a remote peer — unknown consensus item variants,
unbounded outpoint ranges in `await_outputs_outcomes`, unbounded batch
sizes in `await_incoming_contracts`, preimage status queries for
outgoing contracts, and the iroh API paths on both server and gateway.
These now return errors instead.

**Gateway correctness.** `pay_invoice` and direct swaps are made
idempotent (per outgoing contract and per payment hash respectively),
HTLC completion is dispatched by incoming circuit rather than by payment
hash so distinct circuits sharing a hash are all completed, LNv1 gateway
registrations are authenticated, unsafe incoming HTLC expiries are
rejected, and unauthenticated LNv2 routes return errors rather than
panicking.

**Wallet.** Peg-ins claiming an already-tracked UTXO are rejected,
peg-out amounts that overflow the selection arithmetic are rejected, and
peg-out fee rates that cannot produce a real fee are rejected. The
`FM_UNSAFE_ENABLE_RBF_WITHDRAWAL` escape hatch is removed.

One patch from the original set — `fix(wallet): record peg-out change as
an already-claimed peg-in` — is absent here because it has already
landed on `master` via #8938; the diffs were byte-identical.

## Reviewing

The consensus-gated commits deserve the most scrutiny: `feat(lnv1): port
consensus version voting from walletv1`, `feat(ln-server): fund
contracts exactly once from consensus version 2.1`, `feat(ln-server):
bind an incoming contract's ciphertext to its offer`, `feat(ln-server):
require a pending decryption when funding an incoming contract`, and
`feat(wallet): reject unpayable peg-out fee rates from consensus version
2.3`. Please check the activation thresholds and that the pre-activation
path is byte-for-byte the old behaviour, since anything else breaks
replay of historical sessions.

The panic-containment commits are mostly mechanical, but the bounds
chosen for `await_outputs_outcomes` and `await_incoming_contracts` are
judgement calls worth a second opinion.

## Testing

`cargo check --workspace` passes on the rebased branch. The patch set
carries its own tests, including `test(lnv1): cover consensus version
voting reaching activation`, which drives voting through to activation.
Existing module and integration suites cover the touched paths; `git
range-diff` against the pre-rebase branch confirms all 30 commits are
content-identical to their reviewed versions.

Backports to the supported release branches are in the linked PRs.

### Cargo.lock
```diff
@@ -4031,6 +4031,7 @@ dependencies = [
  "async-trait",
  "bitcoin_hashes",
  "erased-serde",
+ "fedimint-api-client",
  "fedimint-core",
  "fedimint-ln-common",
  "fedimint-logging",
```

### fedimint-client-module/src/module/mod.rs
```diff
@@ -842,6 +842,26 @@ where
             .await
     }
 
+    /// Reads an operation log entry within an ongoing database transaction.
+    ///
+    /// Unlike [`Self::get_operation`] this observes writes made earlier in
+    /// `dbtx`, which is what a caller needs to decide atomically whether it is
+    /// about to create an operation that already exists.
+    pub async fn get_operation_dbtx(
+        &self,
+        dbtx: &mut DatabaseTransaction<'_>,
+        operation_id: OperationId,
+    ) -> Option<oplog::OperationLogEntry> {
+        self.client
+            .get()
+            .operation_log()
+            .get_operation_dbtx(
+                &mut dbtx.global_dbtx(self.global_dbtx_access_token),
+                operation_id,
+            )
+            .await
+    }
+
     pub async fn add_operation_log_entry_dbtx(
         &self,
         dbtx: &mut DatabaseTransaction<'_>,
```

### fedimint-core/src/envs.rs
```diff
@@ -83,9 +83,23 @@ pub fn is_running_in_test_env() -> bool {
     unit_test || is_env_var_set("NEXTEST") || is_env_var_set(FM_IN_DEVIMINT_ENV)
 }
 
-/// Use to allow `process_output` to process RBF withdrawal outputs.
-pub fn is_rbf_withdrawal_enabled() -> bool {
-    is_env_var_set("FM_UNSAFE_ENABLE_RBF_WITHDRAWAL")
+/// How long to wait before polling peers for their supported module consensus
+/// version again.
+///
+/// The first poll of a freshly started process races the peers' API servers
+/// binding and normally loses, so a round that failed to reach everyone is
+/// retried soon rather than after the full interval -- otherwise activation is
+/// dead for that interval after every restart. A peer that stays unreachable is
+/// then polled at the short interval indefinitely, which is a few requests per
+/// minute.
+pub fn next_poll_delay(reached_all_peers: bool) -> std::time::Duration {
+    if is_running_in_test_env() {
+        std::time::Duration::from_secs(5)
+    } else if reached_all_peers {
+        std::time::Duration::from_secs(600)
+    } else {
+        std::time::Duration::from_secs(30)
+    }
 }
 
 /// Use to disable automatic consensus version voting for testing and
```

### fedimint-core/src/lib.rs
```diff
@@ -432,6 +432,17 @@ impl IdxRange {
         self.into_iter().count()
     }
 
+    /// Number of indexes in the range, or `None` if the range is descending or
+    /// does not fit into a `usize`.
+    ///
+    /// Ranges are deserialized verbatim from untrusted API requests, so a
+    /// caller validating one has to go through this rather than
+    /// [`Self::count`], which reports a descending range as empty and panics on
+    /// `usize` overflow.
+    pub fn checked_count(self) -> Option<usize> {
+        usize::try_from(self.end.checked_sub(self.start)?).ok()
+    }
+
     pub fn from_inclusive(range: ops::RangeInclusive<u64>) -> Option<Self> {
         range.end().checked_add(1).map(|end| Self {
             start: *range.start(),
@@ -486,6 +497,11 @@ impl OutPointRange {
         self.idx_range.count()
     }
 
+    /// See [`IdxRange::checked_count`].
+    pub fn checked_count(self) -> Option<usize> {
+        self.idx_range.checked_count()
+    }
+
     pub fn start_out_point(self) -> OutPoint {
         OutPoint {
             txid: self.txid,
@@ -581,6 +597,29 @@ impl Feerate {
         let sats = weight_to_vbytes(weight) * self.sats_per_kvb / 1000;
         bitcoin::Amount::from_sat(sats)
     }
+
+    /// Fee for a transaction of the given weight, reproducing the wrapping the
+    /// unchecked multiplication used to do in release profiles.
+    ///
+    /// Consensus behaviour must not depend on the build profile, and
+    /// [`Self::calculate_fee`]'s `*` panics with overflow checks on and wraps
+    /// without them. Sessions ordered before the fee computation was checked
+    /// have to replay as release binaries ran them, so the wrap is explicit.
+    pub fn wrapping_calculate_fee(&self, weight: u64) -> bitcoin::Amount {
+        let sats = weight_to_vbytes(weight).wrapping_mul(self.sats_per_kvb) / 1000;
+        bitcoin::Amount::from_sat(sats)
+    }
+
+    /// Fee for a transaction of the given weight, or `None` if the rate and
+    /// weight do not describe a fee that can exist on chain.
+    ///
+    /// [`Self::calculate_fee`] multiplies unchecked, which wraps to an
+    /// arbitrarily small fee in release profiles. Callers that decide whether
+    /// to accept a transaction must use this instead.
+    pub fn checked_calculate_fee(&self, weight: u64) -> Option<bitcoin::Amount> {
+        let sats = weight_to_vbytes(weight).checked_mul(self.sats_per_kvb)? / 1000;
+        (sats <= bitcoin::Amount::MAX_MONEY.to_sat()).then(|| bitcoin::Amount::from_sat(sats))
+    }
 }
 
 const WITNESS_SCALE_FACTOR: u64 = bitcoin::constants::WITNESS_SCALE_FACTOR as u64;
```

### fedimint-core/src/tests.rs
```diff
@@ -13,6 +13,21 @@ fn calculate_fee() {
     assert_eq!(bitcoin::Amount::from_sat(26), feerate.calculate_fee(101));
 }
 
+#[test]
+fn idx_range_checked_count_rejects_descending_ranges() {
+    use super::IdxRange;
+
+    let range = |start: u64, end: u64| IdxRange::from(start..end);
+
+    assert_eq!(range(3, 7).checked_count(), Some(4));
+    assert_eq!(range(7, 7).checked_count(), Some(0));
+
+    // Descending ranges are silently empty when iterated, which hides a request
+    // we should never be answering in the first place.
+    assert_eq!(range(7, 3).checked_count(), None);
+    assert_eq!(range(u64::MAX, 0).checked_count(), None);
+}
+
 #[test]
 fn test_deserialize_amount_or_all() {
     let all: BitcoinAmountOrAll = serde_json::from_str("\"all\"").unwrap();
```

### fedimint-server/src/consensus/api.rs
```diff
@@ -4,7 +4,7 @@ use std::collections::BTreeMap;
 use std::path::{Path, PathBuf};
 use std::time::Duration;
 
-use anyhow::{Context, Result};
+use anyhow::{Context, Result, ensure};
 use async_trait::async_trait;
 use bitcoin::hashes::sha256;
 use fedimint_api_client::api::{
@@ -80,6 +80,33 @@ use crate::net::api::HasApiContext;
 use crate::net::api::announcement::{ApiAnnouncementKey, ApiAnnouncementPrefix, get_api_urls};
 use crate::net::p2p::P2PStatusReceivers;
 
+/// Maximum number of output outcomes a single `await_outputs_outcomes` request
+/// may ask for. The endpoint is public and unauthenticated and the requested
+/// range is used verbatim to size a `Vec`, so without a cap one request can
+/// trigger a terabyte-scale allocation and abort the guardian process.
+///
+/// Real transactions have a handful of outputs; a client that somehow needs
+/// more can still ask for them one outpoint at a time.
+const MAX_OUTPUTS_OUTCOMES_BATCH: usize = 1024;
+
+/// Number of output outcomes `outpoint_range` asks for, if it is a range we are
+/// willing to serve.
+///
+/// The range is deserialized verbatim from an unauthenticated request, so it
+/// has to be bounded before anything is sized from it.
+fn checked_outputs_outcomes_count(outpoint_range: OutPointRange) -> Result<usize> {
+    let count = outpoint_range
+        .checked_count()
+        .context("Outpoint range is descending or too large")?;
+
+    ensure!(
+        count <= MAX_OUTPUTS_OUTCOMES_BATCH,
+        "Outpoint range must cover at most {MAX_OUTPUTS_OUTCOMES_BATCH} outputs, got {count}"
+    );
+
+    Ok(count)
+}
+
 #[derive(Clone)]
 pub struct ConsensusApi {
     /// Our server configuration
@@ -268,10 +295,14 @@ impl ConsensusApi {
         &self,
         outpoint_range: OutPointRange,
     ) -> Result<Vec<Option<SerdeModuleEncoding<DynOutputOutcome>>>> {
+        // Has to happen before `await_transaction`, which blocks until the
+        // transaction shows up.
+        let count = checked_outputs_outcomes_count(outpoint_range)?;
+
         // Wait for the transaction to be accepted first
         let (module_ids, mut dbtx) = self.await_transaction(outpoint_range.txid()).await;
 
-        let mut outcomes = Vec::with_capacity(outpoint_range.count());
+        let mut outcomes = Vec::with_capacity(count);
 
         for outpoint in outpoint_range {
             let module_id = module_ids
@@ -1173,10 +1204,40 @@ mod tests {
     use fedimint_core::db::IRawDatabaseExt as _;
     use fedimint_core::db::mem_impl::MemDatabase;
     use fedimint_core::net::guardian_metadata::GuardianMetadata;
+    use fedimint_core::{BitcoinHash as _, IdxRange, TransactionId};
 
     use super::*;
     use crate::net::api::guardian_metadata::GuardianMetadataKey;
 
+    /// `AWAIT_OUTPUTS_OUTCOMES` is public and unauthenticated, and the range it
+    /// takes has no validation of its own. A single request used to size a
+    /// `Vec` from `u64::MAX` indexes.
+    #[test]
+    fn outputs_outcomes_range_is_bounded() {
+        let txid = TransactionId::from_slice(&[0; 32]).expect("32 bytes is a valid txid");
+        let range = |start, end| OutPointRange::new(txid, IdxRange::from(start..end));
+
+        assert_eq!(
+            checked_outputs_outcomes_count(range(0, MAX_OUTPUTS_OUTCOMES_BATCH as u64))
+                .expect("a range at the limit is served"),
+            MAX_OUTPUTS_OUTCOMES_BATCH
+        );
+
+        for rejected in [
+            range(0, u64::MAX),
+            range(0, MAX_OUTPUTS_OUTCOMES_BATCH as u64 + 1),
+            // Descending ranges are rejected here rather than left to the
+            // iterator's tolerance of them.
+            range(u64::MAX, 0),
+            range(5, 4),
+        ] {
+            assert!(
+                checked_outputs_outcomes_count(rejected).is_err(),
+                "{rejected:?} must be rejected"
+            );
+        }
+    }
+
     #[tokio::test]
     async fn admin_metadata_update_preserves_persisted_iroh_endpoint() {
         let db: Database = MemDatabase::new().into_database();
```

### fedimint-server/src/consensus/engine.rs
```diff
@@ -1073,12 +1073,16 @@ impl ConsensusEngine {
                 Ok(())
             }
             ConsensusItem::Default { variant, .. } => {
+                // `ConsensusItem` has an `#[encodable_default]` variant, so an unknown
+                // discriminant decodes successfully instead of erroring. The variant byte
+                // is attacker-controlled: a malicious peer can put an arbitrary batch into
+                // its unit, so this must be rejected rather than treated as unreachable.
                 warn!(
                     target: LOG_CONSENSUS,
                     "Minor consensus version mismatch: unexpected consensus item type: {variant}"
                 );
 
-                panic!("Unexpected consensus item type: {variant}")
+                bail!("Unexpected consensus item type: {variant}")
             }
         }
     }
```

### fedimint-server/src/consensus/iroh_api.rs
```diff
@@ -1,4 +1,6 @@
 use std::collections::BTreeMap;
+use std::future::Future;
+use std::panic::AssertUnwindSafe;
 use std::sync::Arc;
 use std::time::Duration;
 
@@ -14,7 +16,7 @@ use iroh::Endpoint;
 use iroh::endpoint::{Incoming, RecvStream, SendStream, VarInt};
 use serde_json::Value;
 use tokio::sync::Semaphore;
-use tracing::warn;
+use tracing::{error, warn};
 
 use super::api::{ConsensusApi, server_endpoints};
 use crate::connection_limits::ConnectionLimits;
@@ -372,30 +374,73 @@ async fn handle_iroh_api_request(
 async fn await_response(api: &IrohApiState, request: IrohApiRequest) -> Result<Value, ApiError> {
     match request.method {
         ApiMethod::Core(method) => {
-            let endpoint = api.core.get(&method).ok_or(ApiError::not_found(method))?;
+            let endpoint = api
+                .core
+                .get(&method)
+                .ok_or_else(|| ApiError::not_found(method.clone()))?;
 
             let (state, context) = api.consensus.context(&request.request, None).await;
 
-            (endpoint.handler)(state, context, request.request).await
+            run_handler(
+                None,
+                &method,
+                (endpoint.handler)(state, context, request.request),
+            )
+            .await
         }
         ApiMethod::Module(module_id, method) => {
             let endpoint = api
                 .modules
                 .get(&module_id)
-                .ok_or(ApiError::not_found(module_id.to_string()))?
+                .ok_or_else(|| ApiError::not_found(module_id.to_string()))?
                 .get(&method)
-                .ok_or(ApiError::not_found(method))?;
+                .ok_or_else(|| ApiError::not_found(method.clone()))?;
 
             let (state, context) = api
                 .consensus
                 .context(&request.request, Some(module_id))
                 .await;
 
-            (endpoint.handler)(state, context, request.request).await
+            run_handler(
+                Some(module_id),
+                &method,
+                (endpoint.handler)(state, context, request.request),
+            )
+            .await
         }
     }
 }
 
+/// Runs an API endpoint handler, turning a panic into an error response for the
+/// caller that triggered it.
+///
+/// Iroh API requests run on the root task group, so an escaping panic would
+/// trip the task group's panic guard and shut the whole guardian down. The
+/// jsonrpsee path contains handler panics the same way.
+async fn run_handler(
+    module_id: Option<ModuleInstanceId>,
+    method: &str,
+    handler: impl Future<Output = Result<Value, ApiError>>,
+) -> Result<Value, ApiError> {
+    // Using `AssertUnwindSafe` here is far from ideal. In theory this means we
+    // could end up with an inconsistent state. In practice most API functions are
+    // only reading and the few that do write anything are atomic. Lastly, this is
+    // only the last line of defense.
+    AssertUnwindSafe(handler)
+        .catch_unwind()
+        .await
+        .unwrap_or_else(|_| {
+            error!(
+                target: LOG_NET_API,
+                module_id = ?module_id,
+                method,
+                "API handler panicked, DO NOT IGNORE, FIX IT!!!"
+            );
+
+            Err(ApiError::server_error("API handler panicked".to_string()))
+        })
+}
+
 // --- iroh-next API endpoint functions ---
 
 pub(super) async fn run_iroh_api_next(
@@ -465,6 +510,23 @@ mod tests {
 
     const TEST_ALPN: &[u8] = b"fedimint-iroh-api-adapter-test";
 
+    #[tokio::test]
+    async fn panicking_handler_returns_an_error_instead_of_unwinding() {
+        let error = run_handler(None, "test_endpoint", async { panic!("handler panic") })
+            .await
+            .expect_err("a panicking handler is reported as a server error");
+
+        assert_eq!(error.code, 500);
+
+        let error = run_handler(Some(3), "test_endpoint", async {
+            panic!("module handler panic")
+        })
+        .await
+        .expect_err("a panicking module handler is reported as a server error");
+
+        assert_eq!(error.code, 500);
+    }
+
     #[tokio::test]
     async fn shared_connection_limit_applies_across_versions() {
         let limit = Arc::new(Semaphore::new(1));
```

### gateway/fedimint-gateway-server/src/federation_manager.rs
```diff
@@ -13,7 +13,7 @@ use fedimint_core::{PeerId, TieredCounts};
 use fedimint_gateway_common::FederationInfo;
 use fedimint_gateway_server_db::GatewayDbtxNcExt as _;
 use fedimint_gw_client::GatewayClientModule;
-use fedimint_gwv2_client::GatewayClientModuleV2;
+use fedimint_gwv2_client::{GatewayClientModuleV2, GatewayOperationMetaV2};
 use fedimint_logging::LOG_GATEWAY;
 use fedimint_mint_client::MintClientModule;
 use tracing::{info, warn};
@@ -111,6 +111,17 @@ impl FederationManager {
                 if let Some(entry) = log_entry {
                     match entry.operation_module_kind() {
                         "lnv2" => {
+                            let Ok(meta) = entry.try_meta::<GatewayOperationMetaV2>() else {
+                                warn!(
+                                    target: LOG_GATEWAY,
+                                    operation_id = %op_id.fmt_short(),
+                                    "Skipping LNv2 operation with invalid metadata while waiting for incoming payments",
+                                );
+                                continue;
+                            };
+                            if !meta.waits_for_completion() {
+                                continue;
+                            }
                             let lnv2 =
                                 client.value().get_first_module::<GatewayClientModuleV2>()?;
                             lnv2.await_completion(op_id).await;
```

### gateway/fedimint-gateway-server/src/iroh_server.rs
```diff
@@ -1,4 +1,5 @@
 use std::collections::{BTreeMap, BTreeSet, HashMap};
+use std::panic::AssertUnwindSafe;
 use std::pin::Pin;
 use std::sync::Arc;
 
@@ -11,11 +12,12 @@ use fedimint_core::net::iroh::build_iroh_endpoint;
 use fedimint_core::task::TaskGroup;
 use fedimint_gateway_common::STOP_ENDPOINT;
 use fedimint_logging::LOG_GATEWAY;
+use futures::FutureExt as _;
 use iroh::endpoint::Incoming;
 use reqwest::StatusCode;
 use serde::de::DeserializeOwned;
 use serde_json::json;
-use tracing::info;
+use tracing::{error, info};
 use url::Url;
 
 use crate::Gateway;
@@ -198,11 +200,14 @@ async fn handle_incoming_iroh_request(
         let request = recv.read_to_end(100_000).await?;
         let request = serde_json::from_slice::<IrohGatewayRequest>(&request)?;
 
-        let (status, body) = handle_request(
-            &request,
-            gateway.clone(),
-            handlers.clone(),
-            task_group.clone(),
+        let (status, body) = run_handler(
+            &request.route,
+            handle_request(
+                &request,
+                gateway.clone(),
+                handlers.clone(),
+                task_group.clone(),
+            ),
         )
         .await?;
 
@@ -218,6 +223,35 @@ async fn handle_incoming_iroh_request(
     Ok(())
 }
 
+/// Runs a request handler, turning a panic into a 500 response for the caller
+/// that triggered it.
+///
+/// Iroh requests are spawned on the gateway's root task group, so a panic
+/// escaping a handler trips the task group's panic guard and shuts the whole
+/// gateway down. The HTTP path does not need this: `axum::serve` spawns its
+/// connection tasks outside any task group, so a panic there only drops that
+/// one connection.
+async fn run_handler(
+    route: &str,
+    handler: impl Future<Output = anyhow::Result<(StatusCode, Json<serde_json::Value>)>>,
+) -> anyhow::Result<(StatusCode, Json<serde_json::Value>)> {
+    // Using `AssertUnwindSafe` here is far from ideal. In theory this means we
+    // could end up with an inconsistent state. In practice this is only the last
+    // line of defense, and losing the gateway process entirely is strictly worse.
+    AssertUnwindSafe(handler)
+        .catch_unwind()
+        .await
+        .unwrap_or_else(|_| {
+            error!(
+                target: LOG_GATEWAY,
+                route,
+                "Gateway API handler panicked, DO NOT IGNORE, FIX IT!!!"
+            );
+
+            Ok((StatusCode::INTERNAL_SERVER_ERROR, Json(json!(()))))
+        })
+}
+
 /// Checks if the requested route is authenticated and will reject the request
 /// if the authentication is incorrect. Then it will lookup the specific handler
 /// in `Handlers`, execute it, and return the function's JSON along with an HTTP
@@ -299,3 +333,17 @@ fn iroh_verify_password(
 
     Err(anyhow!("Invalid password"))
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[tokio::test]
+    async fn panicking_handler_returns_an_error_instead_of_unwinding() {
+        let (status, _body) = run_handler("/pay_invoice", async { panic!("handler panic") })
+            .await
+            .expect("a panicking handler is contained");
+
+        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
+    }
+}
```

### gateway/fedimint-gateway-server/src/lib.rs
```diff
@@ -142,6 +142,10 @@ const DEFAULT_NUM_ROUTE_HINTS: u32 = 1;
 /// Default Bitcoin network for testing purposes.
 pub const DEFAULT_NETWORK: Network = Network::Regtest;
 
+/// How long code that needs to talk to the lightning node backs off before
+/// re-checking whether the gateway has (re)connected to it.
+const LIGHTNING_CONTEXT_RETRY_INTERVAL: Duration = Duration::from_secs(5);
+
 pub type Result<T> = std::result::Result<T, PublicGatewayError>;
 pub type AdminResult<T> = std::result::Result<T, AdminGatewayError>;
 
@@ -1116,7 +1120,7 @@ impl Gateway {
 
         let lnv1_start = fedimint_core::time::now();
         let lnv1_result = self
-            .try_handle_lightning_payment_ln_legacy(&payment_request)
+            .try_handle_lightning_payment_ln_legacy(&payment_request, lightning_context)
             .await;
         let lnv1_outcome = if lnv1_result.is_ok() {
             "success"
@@ -1232,6 +1236,7 @@ impl Gateway {
     async fn try_handle_lightning_payment_ln_legacy(
         &self,
         htlc_request: &InterceptPaymentRequest,
+        lightning_context: &LightningContext,
     ) -> Result<()> {
         // Check if the payment corresponds to a federation supporting legacy Lightning.
         let Some(federation_index) = htlc_request.short_channel_id else {
@@ -1249,6 +1254,10 @@ impl Gateway {
             return Err(PublicGatewayError::LNv1(LNv1Error::IncomingPayment("Incoming payment has a last hop short channel id that does not map to a known federation".to_string())));
         };
 
+        // Both LND's `incoming_expiry` and LDK's `claim_deadline` are absolute
+        // Bitcoin heights. LDK does not currently produce LNv1 forwards (it has
+        // no federation short-channel id), but using the backend's own best
+        // height keeps the unit and chain view consistent for every backend.
         client
             .borrow()
             .with(|client| async {
@@ -1263,7 +1272,12 @@ impl Gateway {
                                         "Federation does not have LNv1 module".to_string(),
                                     ))
                                 })?;
-                        match lnv1.gateway_handle_intercepted_htlc(htlc).await {
+                        match lnv1
+                            .gateway_handle_intercepted_htlc(htlc, async {
+                                Ok(lightning_context.lnrpc.info().await?.block_height)
+                            })
+                            .await
+                        {
                             Ok(_) => Ok(()),
                             Err(e) => Err(PublicGatewayError::LNv1(LNv1Error::IncomingPayment(
                                 format!("Error intercepting lightning payment {e:?}"),
@@ -1360,6 +1374,18 @@ impl Gateway {
         lock.clone()
     }
 
+    /// Drives the gateway's state directly, bypassing the lightning connection
+    /// loop in [`Self::start_gateway`] that owns every real transition.
+    ///
+    /// Tests need to observe behaviour in states the builder cannot start them
+    /// in -- notably "connected later than the federation clients" -- and have
+    /// no lightning node to get there with. Nothing in production should call
+    /// this.
+    #[doc(hidden)]
+    pub async fn set_gateway_state_out_of_band(&self, state: GatewayState) {
+        self.set_gateway_state(state).await;
+    }
+
     /// If the Gateway is connected to the Lightning node, returns the
     /// `ClientConfig` for each federation that the Gateway is connected to.
     pub async fn handle_get_federation_config(
@@ -1772,7 +1798,7 @@ impl Gateway {
                                         routing_fees,
                                         lightning_context.clone(),
                                         registration.endpoint_url,
-                                        registration.keypair.public_key(),
+                                        registration.keypair,
                                     )
                                     .await;
                             }
@@ -1951,8 +1977,14 @@ impl Gateway {
     }
 
     /// Checks the Gateway's current state and returns the proper
-    /// `LightningContext` if it is available. Sometimes the lightning node
-    /// will not be connected and this will return an error.
+    /// `LightningContext` if it is available.
+    ///
+    /// The error is synthesised from the gateway's own state: no RPC is
+    /// attempted, so `Err` means "this process does not currently hold a
+    /// session with the lightning node", never "the lightning node was asked
+    /// and answered no". Callers that would turn a failure here into a
+    /// decision about a payment must use `await_lightning_context`
+    /// instead.
     pub async fn get_lightning_context(
         &self,
     ) -> std::result::Result<LightningContext, LightningRpcError> {
@@ -1963,6 +1995,47 @@ impl Gateway {
         }
     }
 
+    /// Waits until the gateway holds a `LightningContext` and returns it.
+    ///
+    /// The lightning node is the only oracle for whether an HTLC of ours is in
+    /// flight, so code deciding the fate of a payment must actually ask it.
+    /// [`Self::get_lightning_context`] cannot stand in for that: its `Err` is
+    /// produced locally, and the gateway spends part of every startup without
+    /// a context. [`Self::run`] awaits `load_clients` before `start_gateway`,
+    /// and building a client starts its executor, so payment state machines
+    /// persisted across a restart re-enter while the state is still
+    /// `Disconnected`. Reading that as a payment failure cancels an outgoing
+    /// contract whose HTLC the previous process may already have settled,
+    /// leaving the gateway out of pocket for a payment it did make.
+    ///
+    /// Waiting is the conservative side of that trade. It ends when the
+    /// gateway connects, or when the caller is dropped: every caller runs
+    /// inside a client state machine transition or a webserver request, both
+    /// of which are cancelled when the gateway shuts down. It does not strand
+    /// the payer either, since the outgoing contract's timelock refunds them
+    /// without the gateway's cooperation, whereas a cancellation is final (see
+    /// `LightningInput` processing in `fedimint-ln-server`).
+    async fn await_lightning_context(&self) -> LightningContext {
+        loop {
+            match self.get_lightning_context().await {
+                Ok(lightning_context) => return lightning_context,
+                Err(err) => {
+                    let state = self.get_state().await;
+
+                    warn!(
+                        target: LOG_GATEWAY,
+                        err = %err.fmt_compact(),
+                        %state,
+                        retry_interval_secs = LIGHTNING_CONTEXT_RETRY_INTERVAL.as_secs(),
+                        "Not connected to the lightning node, waiting before asking it again",
+                    );
+
+                    sleep(LIGHTNING_CONTEXT_RETRY_INTERVAL).await;
+                }
+            }
+        }
+    }
+
     /// Iterates through all of the federations the gateway is registered with
     /// and requests to remove the registration record.
     pub async fn unannounce_from_all_federations(&self) {
@@ -2280,7 +2353,7 @@ impl IAdminGateway for Gateway {
                     routing_fees,
                     lightning_context.clone(),
                     registration.endpoint_url.clone(),
-                    registration.keypair.public_key(),
+                    registration.keypair,
                 )
                 .await;
             }
@@ -3108,13 +3181,14 @@ impl Gateway {
             .read()
             .await
             .client(federation_id)
-            .map(|client| {
+            .and_then(|client| {
+                // A federation only has to offer one of the two lightning modules, so a
+                // client we serve over LNv1 may well have no LNv2 module at all.
                 client
                     .value()
                     .get_first_module::<GatewayClientModuleV2>()
-                    .expect("Must have client module")
-                    .keypair
-                    .public_key()
+                    .ok()
+                    .map(|module| module.keypair.public_key())
             })
     }
 
@@ -3166,15 +3240,19 @@ impl Gateway {
 
     /// Instructs this gateway to pay a Lightning network invoice via the LNv2
     /// protocol.
-    async fn send_payment_v2(
+    pub async fn send_payment_v2(
         &self,
         payload: SendPaymentPayload,
     ) -> Result<std::result::Result<[u8; 32], Signature>> {
-        self.select_client(payload.federation_id)
-            .await?
+        let client = self.select_client(payload.federation_id).await?;
+        // A federation only has to offer one of the two lightning modules, so a
+        // client we serve over LNv1 may well have no LNv2 module at all.
+        let module = client
             .value()
             .get_first_module::<GatewayClientModuleV2>()
-            .expect("Must have client module")
+            .map_err(|err| PublicGatewayError::LNv2(LNv2Error::OutgoingPayment(err)))?;
+
+        module
             .send_payment(payload)
             .await
             .map_err(LNv2Error::OutgoingPayment)
@@ -3395,35 +3473,45 @@ impl Gateway {
 
 #[async_trait]
 impl IGatewayClientV2 for Gateway {
-    async fn complete_htlc(&self, htlc_response: InterceptPaymentResponse) {
+    async fn complete_htlc(
+        &self,
+        htlc_response: InterceptPaymentResponse,
+    ) -> std::result::Result<(), LightningRpcError> {
         loop {
-            match self.get_lightning_context().await {
-                Ok(lightning_context) => {
-                    match lightning_context
-                        .lnrpc
-                        .complete_htlc(htlc_response.clone())
-                        .await
-                    {
-                        Ok(..) => return,
-                        Err(err) => {
-                            warn!(target: LOG_GATEWAY, err = %err.fmt_compact(), "Failure trying to complete payment");
-                        }
-                    }
+            let lightning_context = self.await_lightning_context().await;
+
+            match lightning_context
+                .lnrpc
+                .complete_htlc(htlc_response.clone())
+                .await
+            {
+                Ok(..) => return Ok(()),
+                Err(err @ LightningRpcError::HtlcCompletionRejected { .. }) => {
+                    warn!(
+                        target: LOG_GATEWAY,
+                        err = %err.fmt_compact(),
+                        "Lightning cannot reach the requested terminal HTLC outcome",
+                    );
+                    return Err(err);
                 }
                 Err(err) => {
                     warn!(target: LOG_GATEWAY, err = %err.fmt_compact(), "Failure trying to complete payment");
                 }
             }
 
-            sleep(Duration::from_secs(5)).await;
+            sleep(LIGHTNING_CONTEXT_RETRY_INTERVAL).await;
         }
     }
 
     async fn is_direct_swap(
         &self,
         invoice: &Bolt11Invoice,
     ) -> anyhow::Result<Option<(IncomingContract, ClientHandleArc)>> {
-        let lightning_context = self.get_lightning_context().await?;
+        // Deciding this from a locally synthesised "not connected" would route a
+        // direct swap onto the lightning network, or -- once the send state
+        // machine turns the error into a cancellation -- forfeit a contract we
+        // may already be committed to. Ask once we can actually answer.
+        let lightning_context = self.await_lightning_context().await;
         if lightning_context.lightning_public_key == invoice.get_payee_pub_key() {
             let (contract, client) = self
                 .get_registered_incoming_contract_and_client_v2(
@@ -3445,7 +3533,9 @@ impl IGatewayClientV2 for Gateway {
         max_delay: u64,
         max_fee: Amount,
     ) -> std::result::Result<[u8; 32], LightningRpcError> {
-        let lightning_context = self.get_lightning_context().await?;
+        // The send state machine forfeits the outgoing contract on any error from
+        // here, so only the lightning node gets to say this payment failed.
+        let lightning_context = self.await_lightning_context().await;
         lightning_context
             .lnrpc
             .pay(invoice, max_delay, max_fee)
@@ -3468,22 +3558,19 @@ impl IGatewayClientV2 for Gateway {
 
     async fn is_lnv1_invoice(&self, invoice: &Bolt11Invoice) -> Option<Spanned<ClientHandleArc>> {
         let rhints = invoice.route_hints();
-        match rhints.first().and_then(|rh| rh.0.last()) {
-            None => None,
-            Some(hop) => match self.get_lightning_context().await {
-                Ok(lightning_context) => {
-                    if hop.src_node_id != lightning_context.lightning_public_key {
-                        return None;
-                    }
+        let hop = rhints.first().and_then(|rh| rh.0.last())?;
 
-                    self.federation_manager
-                        .read()
-                        .await
-                        .get_client_for_index(hop.short_channel_id)
-                }
-                Err(_) => None,
-            },
+        // Answering `None` because we happen to be between lightning connections
+        // sends a swap that never needed the lightning network out over it.
+        let lightning_context = self.await_lightning_context().await;
+        if hop.src_node_id != lightning_context.lightning_public_key {
+            return None;
         }
+
+        self.federation_manager
+            .read()
+            .await
+            .get_client_for_index(hop.short_channel_id)
     }
 
     async fn relay_lnv1_swap(
@@ -3597,9 +3684,9 @@ impl IGatewayClientV1 for Gateway {
     }
 
     async fn verify_pruned_invoice(&self, payment_data: PaymentData) -> anyhow::Result<()> {
-        let lightning_context = self.get_lightning_context().await?;
-
         if matches!(payment_data, PaymentData::PrunedInvoice { .. }) {
+            let lightning_context = self.get_lightning_context().await?;
+
             ensure!(
                 lightning_context.lnrpc.supports_private_payments(),
                 "Private payments are not supported by the lightning node"
@@ -3644,22 +3731,19 @@ impl IGatewayClientV1 for Gateway {
         payment_data: PaymentData,
     ) -> Option<Spanned<ClientHandleArc>> {
         let rhints = payment_data.route_hints();
-        match rhints.first().and_then(|rh| rh.0.last()) {
-            None => None,
-            Some(hop) => match self.get_lightning_context().await {
-                Ok(lightning_context) => {
-                    if hop.src_node_id != lightning_context.lightning_public_key {
-                        return None;
-                    }
+        let hop = rhints.first().and_then(|rh| rh.0.last())?;
 
-                    self.federation_manager
-                        .read()
-                        .await
-                        .get_client_for_index(hop.short_channel_id)
-                }
-                Err(_) => None,
-            },
+        // Answering `None` because we happen to be between lightning connections
+        // sends a swap that never needed the lightning network out over it.
+        let lightning_context = self.await_lightning_context().await;
+        if hop.src_node_id != lightning_context.lightning_public_key {
+            return None;
         }
+
+        self.federation_manager
+            .read()
+            .await
+            .get_client_for_index(hop.short_channel_id)
     }
 
     async fn pay(
@@ -3668,7 +3752,9 @@ impl IGatewayClientV1 for Gateway {
         max_delay: u64,
         max_fee: Amount,
     ) -> std::result::Result<PayInvoiceResponse, LightningRpcError> {
-        let lightning_context = self.get_lightning_context().await?;
+        // `GatewayPayInvoice` cancels the outgoing contract on any error from
+        // here, so only the lightning node gets to say this payment failed.
+        let lightning_context = self.await_lightning_context().await;
 
         match payment_data {
             PaymentData::Invoice(invoice) => {
@@ -3691,15 +3777,7 @@ impl IGatewayClientV1 for Gateway {
         htlc: InterceptPaymentResponse,
     ) -> std::result::Result<(), LightningRpcError> {
         // Wait until the lightning node is online to complete the HTLC.
-        let lightning_context = loop {
-            match self.get_lightning_context().await {
-                Ok(lightning_context) => break lightning_context,
-                Err(err) => {
-                    warn!(target: LOG_GATEWAY, err = %err.fmt_compact(), "Failure trying to complete payment");
-                    sleep(Duration::from_secs(5)).await;
-                }
-            }
-        };
+        let lightning_context = self.await_lightning_context().await;
 
         lightning_context.lnrpc.complete_htlc(htlc).await
     }
```

### gateway/fedimint-gateway-server/tests/tests.rs
```diff
@@ -19,24 +19,28 @@ use fedimint_core::module::{AmountUnit, Amounts};
 use fedimint_core::task::{TaskGroup, sleep_in_test, timeout};
 use fedimint_core::time::now;
 use fedimint_core::util::{NextOrPending, backoff_util, retry};
-use fedimint_core::{Amount, OutPoint, msats, sats, secp256k1};
+use fedimint_core::{Amount, OutPoint, TransactionId, msats, sats, secp256k1};
 use fedimint_dummy_client::{DummyClientInit, DummyClientModule};
 use fedimint_dummy_server::DummyInit;
 use fedimint_eventlog::Event;
 use fedimint_gateway_common::{PaymentLogPayload, SetFeesPayload};
-use fedimint_gateway_server::Gateway;
+use fedimint_gateway_server::{Gateway, GatewayState};
 use fedimint_gateway_ui::IAdminGateway;
 use fedimint_gw_client::pay::{
     OutgoingContractError, OutgoingPaymentError, OutgoingPaymentErrorType,
 };
 use fedimint_gw_client::{
     GatewayClientModule, GatewayExtPayStates, GatewayExtReceiveStates, GatewayMeta, Htlc,
+    SwapParameters,
 };
 use fedimint_gwv2_client::events::{
     CompleteLightningPaymentSucceeded, IncomingPaymentStarted, IncomingPaymentSucceeded,
     OutgoingPaymentStarted, OutgoingPaymentSucceeded,
 };
-use fedimint_gwv2_client::{FinalReceiveState, GatewayClientModuleV2};
+use fedimint_gwv2_client::{
+    FinalReceiveState, GatewayClientModuleV2, GatewayClientStateMachinesV2, GatewayOperationMetaV2,
+    IncomingCircuitKey,
+};
 use fedimint_ln_client::api::LnFederationApi;
 use fedimint_ln_client::pay::{PayInvoicePayload, PaymentData};
 use fedimint_ln_client::{
@@ -51,8 +55,9 @@ use fedimint_ln_common::contracts::{
 };
 use fedimint_ln_common::{LightningGateway, LightningInput, LightningOutput, PrunedInvoice};
 use fedimint_ln_server::LightningInit;
+use fedimint_lnv2_common::LightningInvoice;
 use fedimint_lnv2_common::contracts::{IncomingContract, OutgoingContract, PaymentImage};
-use fedimint_lnv2_common::gateway_api::PaymentFee;
+use fedimint_lnv2_common::gateway_api::{PaymentFee, SendPaymentPayload};
 use fedimint_logging::LOG_TEST;
 use fedimint_testing::btc::BitcoinTest;
 use fedimint_testing::db::BYTE_33;
@@ -545,7 +550,7 @@ async fn test_gateway_client_intercept_valid_htlc() -> anyhow::Result<()> {
         };
         let intercept_op = gateway_client
             .get_first_module::<GatewayClientModule>()?
-            .gateway_handle_intercepted_htlc(htlc)
+            .gateway_handle_intercepted_htlc(htlc, async { Ok(0) })
             .await?;
         let mut intercept_sub = gateway_client
             .get_first_module::<GatewayClientModule>()?
@@ -609,7 +614,7 @@ async fn test_gateway_shutdown_completes_in_flight_payment() -> anyhow::Result<(
         };
         let intercept_op = gateway_client
             .get_first_module::<GatewayClientModule>()?
-            .gateway_handle_intercepted_htlc(htlc)
+            .gateway_handle_intercepted_htlc(htlc, async { Ok(0) })
             .await?;
         let mut intercept_sub = gateway_client
             .get_first_module::<GatewayClientModule>()?
@@ -650,6 +655,91 @@ async fn test_gateway_shutdown_completes_in_flight_payment() -> anyhow::Result<(
     .await
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_client_intercept_enforces_expiry_boundary() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_id = gateway.http_gateway_id().await;
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+        let initial_gateway_balance = sats(1000);
+        gateway_client
+            .get_first_module::<DummyClientModule>()?
+            .mock_receive(initial_gateway_balance, AmountUnit::BITCOIN)
+            .await?;
+
+        let invoice_amount = sats(100);
+        let ln_module = user_client.get_first_module::<LightningClientModule>()?;
+        let lightning_gateway = ln_module.select_gateway(&gateway_id).await;
+        let (_invoice_op, invoice, _) = ln_module
+            .create_bolt11_invoice(
+                invoice_amount,
+                Bolt11InvoiceDescription::Direct(Description::new("expiry boundary".to_string())?),
+                None,
+                "test intercept HTLC expiry boundary",
+                lightning_gateway,
+            )
+            .await?;
+        let route_hints = invoice.route_hints();
+        let route_hint_last_hops = route_hints
+            .iter()
+            .filter_map(|route_hint| route_hint.0.last())
+            .collect::<Vec<_>>();
+        assert!(!route_hint_last_hops.is_empty());
+        assert!(route_hint_last_hops.iter().all(|hop| {
+            hop.cltv_expiry_delta == fedimint_ln_common::LNV1_INCOMING_HTLC_ADVERTISED_EXPIRY_DELTA
+        }));
+
+        let current_block_height = 1_000;
+        let htlc = Htlc {
+            payment_hash: *invoice.payment_hash(),
+            incoming_amount_msat: invoice_amount,
+            outgoing_amount_msat: invoice_amount,
+            incoming_expiry: current_block_height
+                + fedimint_gw_client::LNV1_HTLC_EXPIRY_SAFETY_MARGIN,
+            short_channel_id: Some(1),
+            incoming_chan_id: 2,
+            htlc_id: 1,
+        };
+        let gateway_ln_module = gateway_client.get_first_module::<GatewayClientModule>()?;
+
+        let err = gateway_ln_module
+            .gateway_handle_intercepted_htlc(htlc.clone(), async { Ok(current_block_height) })
+            .await
+            .expect_err("HTLC at the expiry boundary must be rejected");
+        assert!(err.to_string().contains("incoming HTLC expiry is unsafe"));
+        assert_eq!(
+            gateway_client.get_balance_for_btc().await?,
+            initial_gateway_balance
+        );
+
+        let accepted_htlc = Htlc {
+            incoming_expiry: htlc.incoming_expiry + 1,
+            ..htlc
+        };
+        let operation_id = gateway_ln_module
+            .gateway_handle_intercepted_htlc(accepted_htlc, async { Ok(current_block_height) })
+            .await?;
+        let mut receive_updates = gateway_ln_module
+            .gateway_subscribe_ln_receive(operation_id)
+            .await?
+            .into_stream();
+        assert_eq!(
+            receive_updates.ok().await?,
+            GatewayExtReceiveStates::Funding
+        );
+        assert_matches!(
+            receive_updates.ok().await?,
+            GatewayExtReceiveStates::Preimage { .. }
+        );
+        assert_eq!(
+            gateway_client.get_balance_for_btc().await?,
+            initial_gateway_balance.saturating_sub(invoice_amount)
+        );
+
+        Ok(())
+    })
+    .await
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn test_gateway_client_intercept_same_circuit_replay_is_idempotent() -> anyhow::Result<()> {
     single_federation_test(|gateway, _, fed, user_client, _| async move {
@@ -680,21 +770,28 @@ async fn test_gateway_client_intercept_same_circuit_replay_is_idempotent() -> an
             payment_hash: *invoice.payment_hash(),
             incoming_amount_msat: Amount::from_msats(invoice.amount_milli_satoshis().unwrap()),
             outgoing_amount_msat: Amount::from_msats(invoice.amount_milli_satoshis().unwrap()),
-            incoming_expiry: u32::MAX,
+            incoming_expiry: fedimint_gw_client::LNV1_HTLC_EXPIRY_SAFETY_MARGIN + 1,
             short_channel_id: Some(1),
             incoming_chan_id: 2,
             htlc_id: 1,
         };
 
         let gateway_ln_module = gateway_client.get_first_module::<GatewayClientModule>()?;
         let (first, second) = tokio::join!(
-            gateway_ln_module.gateway_handle_intercepted_htlc(htlc.clone()),
-            gateway_ln_module.gateway_handle_intercepted_htlc(htlc.clone()),
+            gateway_ln_module.gateway_handle_intercepted_htlc(htlc.clone(), async { Ok(0) }),
+            gateway_ln_module.gateway_handle_intercepted_htlc(htlc.clone(), async { Ok(0) }),
         );
         let first_op = first?;
         let second_op = second?;
         assert_eq!(first_op, second_op);
 
+        let active_replay_op = gateway_ln_module
+            .gateway_handle_intercepted_htlc(htlc.clone(), async {
+                anyhow::bail!("backend info must not be queried for active replay")
+            })
+            .await?;
+        assert_eq!(first_op, active_replay_op);
+
         let mut intercept_sub = gateway_ln_module
             .gateway_subscribe_ln_receive(first_op)
             .await?
@@ -711,9 +808,15 @@ async fn test_gateway_client_intercept_same_circuit_replay_is_idempotent() -> an
         gateway_ln_module.await_completion(first_op).await;
 
         let terminal_replay_op = gateway_ln_module
-            .gateway_handle_intercepted_htlc(htlc)
+            .gateway_handle_intercepted_htlc(htlc, async {
+                anyhow::bail!("backend info must not be queried for inactive replay")
+            })
             .await?;
         assert_eq!(first_op, terminal_replay_op);
+        assert_eq!(
+            initial_gateway_balance.saturating_sub(invoice_amount),
+            gateway_client.get_balance_for_btc().await?
+        );
 
         Ok(())
     })
@@ -745,7 +848,7 @@ async fn test_gateway_client_intercept_offer_does_not_exist() -> anyhow::Result<
 
         match gateway_client
             .get_first_module::<GatewayClientModule>()?
-            .gateway_handle_intercepted_htlc(htlc)
+            .gateway_handle_intercepted_htlc(htlc, async { Ok(0) })
             .await
         {
             Ok(_) => panic!(
@@ -792,7 +895,7 @@ async fn test_gateway_client_intercept_htlc_no_funds() -> anyhow::Result<()> {
         // Attempt to route an HTLC while the gateway has no funds
         match gateway_client
             .get_first_module::<GatewayClientModule>()?
-            .gateway_handle_intercepted_htlc(htlc)
+            .gateway_handle_intercepted_htlc(htlc, async { Ok(0) })
             .await
         {
             Ok(_) => panic!("Expected incoming offer validation to fail due to lack of funds"),
@@ -888,7 +991,7 @@ async fn test_gateway_client_intercept_htlc_invalid_offer() -> anyhow::Result<()
 
             let intercept_op = gateway_client
                 .get_first_module::<GatewayClientModule>()?
-                .gateway_handle_intercepted_htlc(htlc)
+                .gateway_handle_intercepted_htlc(htlc, async { Ok(0) })
                 .await?;
             let mut intercept_sub = gateway_client
                 .get_first_module::<GatewayClientModule>()?
@@ -1334,6 +1437,121 @@ async fn lnv2_incoming_contract_with_invalid_preimage_is_refunded() -> anyhow::R
     Ok(())
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn lnv2_relay_persists_every_distinct_incoming_circuit() -> anyhow::Result<()> {
+    let fixtures = fixtures();
+    let fed = fixtures.new_fed_degraded().await;
+    let gateway = fixtures.new_gateway().await;
+    fed.connect_gateway(&gateway).await;
+    send_msats_to_gateway(&gateway, fed.id(), 1_000_000_000).await;
+
+    let client = gateway.select_client(fed.id()).await?.into_value();
+    let module = client.get_first_module::<GatewayClientModuleV2>()?;
+    let preimage = [23; 32];
+    let payment_hash = preimage.consensus_hash();
+    let contract = IncomingContract::new(
+        module.cfg.tpe_agg_pk,
+        [42; 32],
+        preimage,
+        PaymentImage::Hash(payment_hash),
+        Amount::from_sats(1000),
+        u64::MAX,
+        Keypair::new(secp256k1::SECP256K1, &mut rand::thread_rng()).public_key(),
+        module.keypair.public_key(),
+        Keypair::new(secp256k1::SECP256K1, &mut rand::thread_rng()).public_key(),
+    );
+    let receive_operation_id = OperationId::from_encodable(&contract);
+    let completion_id = |circuit: IncomingCircuitKey| {
+        OperationId::from_encodable(&(
+            "gateway-lnv2-incoming-circuit",
+            receive_operation_id,
+            circuit,
+        ))
+    };
+    let hold = IncomingCircuitKey {
+        incoming_chan_id: 0,
+        htlc_id: 0,
+    };
+    let forward = IncomingCircuitKey {
+        incoming_chan_id: 42,
+        htlc_id: 7,
+    };
+
+    let (hold_result, forward_result) = tokio::join!(
+        module.relay_incoming_htlc(
+            payment_hash,
+            hold.incoming_chan_id,
+            hold.htlc_id,
+            contract.clone(),
+            1_000_000,
+        ),
+        module.relay_incoming_htlc(
+            payment_hash,
+            forward.incoming_chan_id,
+            forward.htlc_id,
+            contract.clone(),
+            1_000_000,
+        ),
+    );
+    hold_result?;
+    forward_result?;
+
+    // Same-circuit replay must not add another operation or state machine.
+    module
+        .relay_incoming_htlc(
+            payment_hash,
+            forward.incoming_chan_id,
+            forward.htlc_id,
+            contract,
+            1_000_000,
+        )
+        .await?;
+
+    let receive_entry = client
+        .operation_log()
+        .get_operation(receive_operation_id)
+        .await
+        .expect("receive operation must be persisted");
+    assert!(
+        !receive_entry
+            .meta::<GatewayOperationMetaV2>()
+            .waits_for_completion()
+    );
+
+    for circuit in [hold, forward] {
+        let operation_id = completion_id(circuit);
+        let entry = client
+            .operation_log()
+            .get_operation(operation_id)
+            .await
+            .expect("circuit completion operation must be persisted");
+        assert!(
+            entry
+                .meta::<GatewayOperationMetaV2>()
+                .waits_for_completion()
+        );
+
+        let active = module
+            .client_ctx
+            .get_own_operation_active_states(operation_id)
+            .await;
+        let inactive = module
+            .client_ctx
+            .get_own_operation_inactive_states(operation_id)
+            .await;
+        assert_eq!(active.len() + inactive.len(), 1);
+        assert!(
+            active
+                .into_iter()
+                .map(|(state, _)| state)
+                .chain(inactive.into_iter().map(|(state, _)| state))
+                .all(|state| matches!(state, GatewayClientStateMachinesV2::CircuitComplete(_)))
+        );
+    }
+
+    Ok(())
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn lnv2_expired_incoming_contract_is_rejected() -> anyhow::Result<()> {
     let fixtures = fixtures();
@@ -1637,3 +1855,401 @@ async fn gateway_read_payment_log() -> anyhow::Result<()> {
 
     Ok(())
 }
+
+/// A federation only has to offer one of the two lightning modules, so a
+/// gateway routinely serves federations with an LNv1 module and no LNv2 one.
+fn lnv1_only_fixtures() -> Fixtures {
+    Fixtures::new_primary(DummyClientInit, DummyInit)
+        .with_server_only_module(UnknownInit)
+        .with_module(
+            LightningClientInit {
+                gateway_conn: Some(Arc::new(MockGatewayConnection)),
+            },
+            LightningInit,
+        )
+}
+
+/// The LNv2 routes are registered unauthenticated, so anyone can point them at
+/// any federation the gateway serves. Looking up the LNv2 client module used to
+/// `expect` it into existence, which panics for an LNv1-only federation and
+/// takes the gateway process down with it over iroh.
+#[tokio::test(flavor = "multi_thread")]
+async fn lnv2_routes_reject_a_federation_without_an_lnv2_module() -> anyhow::Result<()> {
+    let fixtures = lnv1_only_fixtures();
+    let fed = fixtures.new_fed_degraded().await;
+    let gateway = fixtures.new_gateway().await;
+    fed.connect_gateway(&gateway).await;
+
+    assert!(
+        gateway.routing_info_v2(&fed.id()).await?.is_none(),
+        "a federation without an LNv2 module has no LNv2 routing info"
+    );
+
+    let keypair = Keypair::new(secp256k1::SECP256K1, &mut rand::thread_rng());
+    let payload = SendPaymentPayload {
+        federation_id: fed.id(),
+        outpoint: OutPoint {
+            txid: TransactionId::from_slice(&[0; 32]).expect("32 bytes is a valid txid"),
+            out_idx: 0,
+        },
+        contract: OutgoingContract {
+            payment_image: PaymentImage::Hash([0_u8; 32].consensus_hash()),
+            amount: Amount::from_msats(1000),
+            expiration: 120,
+            claim_pk: keypair.public_key(),
+            refund_pk: keypair.public_key(),
+            ephemeral_pk: keypair.public_key(),
+        },
+        invoice: LightningInvoice::Bolt11(FakeLightningTest::new().invoice(sats(1), None)?),
+        auth: secp256k1::SECP256K1
+            .sign_schnorr(&secp256k1::Message::from_digest([0; 32]), &keypair),
+    };
+
+    assert!(
+        gateway.send_payment_v2(payload).await.is_err(),
+        "a federation without an LNv2 module cannot be asked to send an LNv2 payment"
+    );
+
+    Ok(())
+}
+
+/// An amountless BOLT11 invoice is rejected by `validate_outgoing_account`, but
+/// the operation log entry written when the payment starts needs the amount
+/// before the state machine ever gets that far, and used to `expect` it.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_client_rejects_amountless_invoice() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+
+        let ctx = secp256k1::Secp256k1::new();
+        let keypair = Keypair::new(&ctx, &mut rand::thread_rng());
+        let amountless_invoice =
+            lightning_invoice::InvoiceBuilder::new(lightning_invoice::Currency::Regtest)
+                .description(String::new())
+                .payment_hash(sha256(&[0; 32]))
+                .current_timestamp()
+                .min_final_cltv_expiry_delta(0)
+                .payment_secret(lightning_invoice::PaymentSecret([0; 32]))
+                .build_signed(|m| ctx.sign_ecdsa_recoverable(m, &keypair.secret_key()))?;
+
+        let error = gateway_client
+            .get_first_module::<GatewayClientModule>()?
+            .gateway_pay_bolt11_invoice(PayInvoicePayload {
+                federation_id: user_client.federation_id(),
+                contract_id: sha256(&[0; 32]).into(),
+                payment_data: PaymentData::Invoice(amountless_invoice),
+                preimage_auth: Hash::hash(&[0; 32]),
+            })
+            .await
+            .expect_err("an invoice without an amount is rejected");
+
+        assert_eq!(
+            error.downcast::<OutgoingContractError>()?,
+            OutgoingContractError::InvoiceMissingAmount
+        );
+
+        Ok(())
+    })
+    .await
+}
+
+/// `pay_invoice` is unauthenticated and keys its operation on the contract id,
+/// but the state machine's dedupe key covers the whole payload, so a second
+/// request that differs only in `preimage_auth` slips past it. That used to
+/// panic on the duplicate operation log entry, taking the gateway down.
+///
+/// Not panicking is not enough on its own: nothing else pins a contract to a
+/// single payment attempt, so the duplicate has to be recognised as one and
+/// answered with the operation already in flight rather than buying the
+/// preimage a second time out of the gateway's own funds.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_client_pay_invoice_is_idempotent_per_contract() -> anyhow::Result<()> {
+    single_federation_test(
+        |gateway, other_lightning_client, fed, user_client, _| async move {
+            let gateway_id = gateway.http_gateway_id().await;
+            let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+
+            let dummy_module = user_client.get_first_module::<DummyClientModule>()?;
+            dummy_module
+                .mock_receive(sats(1000), AmountUnit::BITCOIN)
+                .await?;
+
+            let lightning_module = user_client.get_first_module::<LightningClientModule>()?;
+            let invoice = other_lightning_client.invoice(sats(250), None)?;
+            let selected_gateway = lightning_module.select_gateway(&gateway_id).await;
+
+            let OutgoingLightningPayment {
+                payment_type,
+                contract_id,
+                fee: _,
+            } = user_pay_invoice(&lightning_module, invoice.clone(), &gateway_id).await?;
+            let PayType::Lightning(pay_op) = payment_type else {
+                panic!("Expected Lightning payment!");
+            };
+            let mut pay_sub = lightning_module
+                .subscribe_ln_pay(pay_op)
+                .await?
+                .into_stream();
+            assert_eq!(pay_sub.ok().await?, LnPayState::Created);
+            assert_matches!(pay_sub.ok().await?, LnPayState::Funded { .. });
+
+            let payload = |preimage_auth| PayInvoicePayload {
+                federation_id: user_client.federation_id(),
+                contract_id,
+                payment_data: get_payment_data(selected_gateway.clone(), invoice.clone()),
+                preimage_auth,
+            };
+
+            let gateway_module = gateway_client.get_first_module::<GatewayClientModule>()?;
+            let first = gateway_module
+                .gateway_pay_bolt11_invoice(payload(Hash::hash(&[0; 32])))
+                .await?;
+            // Same contract, different `preimage_auth`: a distinct state machine
+            // state, so the executor's dedupe does not catch this one.
+            let second = gateway_module
+                .gateway_pay_bolt11_invoice(payload(Hash::hash(&[1; 32])))
+                .await?;
+
+            assert_eq!(
+                first, second,
+                "the duplicate request joins the payment already in flight"
+            );
+            assert_eq!(
+                gateway_client
+                    .operation_log()
+                    .paginate_operations_rev(10, None)
+                    .await
+                    .len(),
+                1,
+                "the duplicate request must not start a second payment for the contract"
+            );
+
+            let mut gw_pay_sub = gateway_module
+                .gateway_subscribe_ln_pay(first)
+                .await?
+                .into_stream();
+            assert_eq!(gw_pay_sub.ok().await?, GatewayExtPayStates::Created);
+            assert_matches!(gw_pay_sub.ok().await?, GatewayExtPayStates::Preimage { .. });
+            assert_matches!(gw_pay_sub.ok().await?, GatewayExtPayStates::Success { .. });
+
+            // One purchase of the preimage, so exactly one claim of the contract.
+            let outgoing_fee = gateway
+                .handle_get_info()
+                .await?
+                .federations
+                .first()
+                .expect("Only one federation")
+                .config
+                .lightning_fee
+                .fee(250_000);
+            assert_eq!(
+                gateway_client.get_balance_for_btc().await?,
+                sats(250)
+                    .checked_add(outgoing_fee)
+                    .expect("Should not wrap around")
+            );
+
+            Ok(())
+        },
+    )
+    .await
+}
+
+/// `Gateway::run` awaits `load_clients` before `start_gateway`, and building a
+/// federation client starts its executor, so a `PayInvoice` state machine that
+/// was persisted before a restart runs again while the gateway is still
+/// `Disconnected`. `get_lightning_context` then reports `FailedToConnect`
+/// without any RPC having been attempted, and the send path used to read that
+/// local verdict as the lightning node refusing the payment: it cancelled the
+/// outgoing contract, refunding a sender whose HTLC the previous process may
+/// already have settled and leaving the gateway short the difference.
+///
+/// Only the lightning node knows whether an HTLC of ours is in flight, so the
+/// gateway has to wait until it can ask, rather than answer for it.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_waits_to_reach_lightning_before_cancelling_outgoing_payment()
+-> anyhow::Result<()> {
+    single_federation_test(
+        |gateway, other_lightning_client, fed, user_client, _| async move {
+            let gateway_id = gateway.http_gateway_id().await;
+            let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+            user_client
+                .get_first_module::<DummyClientModule>()?
+                .mock_receive(sats(1000), AmountUnit::BITCOIN)
+                .await?;
+
+            let lightning_module = user_client.get_first_module::<LightningClientModule>()?;
+            let invoice = other_lightning_client.invoice(sats(250), None)?;
+
+            let OutgoingLightningPayment {
+                payment_type,
+                contract_id,
+                fee: _,
+            } = user_pay_invoice(&lightning_module, invoice.clone(), &gateway_id).await?;
+            let PayType::Lightning(pay_op) = payment_type else {
+                panic!("Expected Lightning payment!");
+            };
+            let mut pay_sub = lightning_module
+                .subscribe_ln_pay(pay_op)
+                .await?
+                .into_stream();
+            assert_eq!(pay_sub.ok().await?, LnPayState::Created);
+            assert_matches!(pay_sub.ok().await?, LnPayState::Funded { .. });
+
+            // Stand in for the restart: the outgoing contract is funded and the
+            // gateway's state machine is about to run against a gateway that has
+            // not (re-)established its lightning session yet.
+            let lightning_context = gateway.get_lightning_context().await?;
+            gateway
+                .set_gateway_state_out_of_band(GatewayState::Disconnected)
+                .await;
+
+            let gateway_module = gateway_client.get_first_module::<GatewayClientModule>()?;
+            let operation_id = gateway_module
+                .gateway_pay_bolt11_invoice(PayInvoicePayload {
+                    federation_id: user_client.federation_id(),
+                    contract_id,
+                    payment_data: PaymentData::Invoice(invoice),
+                    preimage_auth: Hash::hash(&[0; 32]),
+                })
+                .await?;
+            let mut gw_pay_sub = gateway_module
+                .gateway_subscribe_ln_pay(operation_id)
+                .await?
+                .into_stream();
+            assert_eq!(gw_pay_sub.ok().await?, GatewayExtPayStates::Created);
+
+            // Any verdict reached here is one the lightning node was never asked
+            // for, and a cancellation cannot be taken back.
+            if let Ok(state) = fedimint_core::task::timeout(
+                Duration::from_secs(5),
+                futures::StreamExt::next(&mut gw_pay_sub),
+            )
+            .await
+            {
+                panic!(
+                    "Gateway settled the fate of an outgoing payment while not connected to its lightning node: {state:?}"
+                );
+            }
+
+            // Reconnected, the payment resolves the way it always should have.
+            gateway
+                .set_gateway_state_out_of_band(GatewayState::Running { lightning_context })
+                .await;
+
+            assert_matches!(gw_pay_sub.ok().await?, GatewayExtPayStates::Preimage { .. });
+            assert_matches!(gw_pay_sub.ok().await?, GatewayExtPayStates::Success { .. });
+
+            Ok(())
+        },
+    )
+    .await
+}
+
+/// A direct swap is the other half of an outgoing contract in a second
+/// federation: the gateway funds an incoming contract here to buy the preimage
+/// that claims that contract. `gateway_handle_direct_swap` used to have no
+/// idempotency guard, so a `GatewayPayInvoice` state machine re-entering after
+/// a gateway restart tried to fund the swap a second time. Funding consumed the
+/// federation's offer the first time round, so the retry fails -- either
+/// waiting out `fetch_and_validate_offer` or bailing on the operation that
+/// already exists -- and `buy_preimage_via_direct_swap` reads that as
+/// `SwapFailed` and cancels the outgoing contract. The sender is refunded while
+/// the recipient is still paid out of the incoming contract the gateway funded.
+///
+/// The second call has nothing left to fund and everything to gain from the
+/// preimage the first one is buying, so hand it that operation.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_client_direct_swap_reentry_joins_the_funded_swap() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_id = gateway.http_gateway_id().await;
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+        let initial_gateway_balance = sats(1000);
+        gateway_client
+            .get_first_module::<DummyClientModule>()?
+            .mock_receive(initial_gateway_balance, AmountUnit::BITCOIN)
+            .await?;
+
+        let invoice_amount = sats(100);
+        let ln_module = user_client.get_first_module::<LightningClientModule>()?;
+        let lightning_gateway = ln_module.select_gateway(&gateway_id).await;
+        let (_invoice_op, invoice, _) = ln_module
+            .create_bolt11_invoice(
+                invoice_amount,
+                Bolt11InvoiceDescription::Direct(Description::new("direct swap".to_string())?),
+                None,
+                "test direct swap re-entry",
+                lightning_gateway,
+            )
+            .await?;
+
+        let swap_params = SwapParameters {
+            payment_hash: *invoice.payment_hash(),
+            amount_msat: invoice_amount,
+        };
+        let gateway_module = gateway_client.get_first_module::<GatewayClientModule>()?;
+        let first = gateway_module
+            .gateway_handle_direct_swap(swap_params.clone())
+            .await?;
+        let mut receive_sub = gateway_module
+            .gateway_subscribe_ln_receive(first)
+            .await?
+            .into_stream();
+        assert_eq!(receive_sub.ok().await?, GatewayExtReceiveStates::Funding);
+        assert_matches!(
+            receive_sub.ok().await?,
+            GatewayExtReceiveStates::Preimage { .. }
+        );
+
+        // The restart: the same swap is asked for again, with the offer that
+        // funded it already consumed.
+        let second = fedimint_core::task::timeout(
+            Duration::from_secs(30),
+            gateway_module.gateway_handle_direct_swap(swap_params),
+        )
+        .await
+        .expect("a re-entrant direct swap must not wait on the offer it already consumed")?;
+
+        assert_eq!(
+            first, second,
+            "the re-entrant swap joins the operation already holding the preimage"
+        );
+        assert_eq!(
+            gateway_client.get_balance_for_btc().await?,
+            initial_gateway_balance.saturating_sub(invoice_amount),
+            "the incoming contract must only be funded once"
+        );
+
+        // The check above the funding helper cannot settle a race on its own, so
+        // two callers that both get past it must still end up on one operation.
+        let (_invoice_op, concurrent_invoice, _) = ln_module
+            .create_bolt11_invoice(
+                invoice_amount,
+                Bolt11InvoiceDescription::Direct(Description::new("concurrent".to_string())?),
+                None,
+                "test concurrent direct swap",
+                ln_module.select_gateway(&gateway_id).await,
+            )
+            .await?;
+        let concurrent_swap_params = SwapParameters {
+            payment_hash: *concurrent_invoice.payment_hash(),
+            amount_msat: invoice_amount,
+        };
+        let (left, right) = tokio::join!(
+            gateway_module.gateway_handle_direct_swap(concurrent_swap_params.clone()),
+            gateway_module.gateway_handle_direct_swap(concurrent_swap_params),
+        );
+        assert_eq!(
+            left?, right?,
+            "concurrent requests for one swap must share the single funded operation"
+        );
+        assert_eq!(
+            gateway_client.get_balance_for_btc().await?,
+            initial_gateway_balance.saturating_sub(invoice_amount + invoice_amount),
+            "the second swap's incoming contract must also only be funded once"
+        );
+
+        Ok(())
+    })
+    .await
+}
```
