# [?] fix(eth-proof-manager): three correctness fixes for validation retries, metrics labels, and verifier panics (#4723)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-15
Source: https://github.com/matter-labs/zksync-era/commit/d88daa4540cf6089946ad0411c2f9c544d919054
Type: security-commit

## Details
fix(eth-proof-manager): three correctness fixes for validation retries, metrics labels, and verifier panics (#4723)

Three bug fixes for the `eth_proof_manager` node component.

## Fix 1 — Validation tx retries after first tx was already confirmed

When `send_tx` timed out polling for a receipt, it discarded the
broadcast hash. The retry re-queried the nonce, saw it had advanced
(original tx was mined), and sent a new tx against the next nonce slot —
which reverted on-chain since the validation was already submitted. The
batch stayed `Proven` in the DB and the loop kept retrying until
`validation_tx_attempts` was exhausted.

`send_tx` now returns the broadcast hash alongside any receipt-timeout
error. `send_tx_with_retries` checks all pending hashes for confirmation
before sending a replacement.

## Fix 2 — Truncated addresses in Prometheus labels

`Address` (`H160`) `Display` truncates to `0x<2 bytes>…<2 bytes>`. Both
address label values were set via `.to_string()`, producing e.g.
`0x1a2b…ef01` instead of the full address. Changed to `format!("{:#x}",
addr)`.

## Fix 3 — Verifier and event-handler panics crash the component

`fflonk::verify` can panic on malformed proof data (field elements out
of range). Several `panic!` calls in both event handlers fired on
unexpected ABI token values or unknown `ProvingNetwork` discriminants.
All panics inside the task caused a restart loop instead of marking the
proof invalid.

- `fflonk::verify` wrapped in
`std::panic::catch_unwind(AssertUnwindSafe(...))`.
- `panic!` calls in handlers replaced with `anyhow::bail!`.
- `ProvingNetwork::from_u256` changed to return `anyhow::Result<Self>`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: afo <afo@matter-labs.io>
Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

### core/node/eth_proof_manager/src/client.rs
```diff
@@ -122,28 +122,85 @@ impl ProofManagerClient {
         let mut prev_priority_fee_per_gas: Option<u64> = None;
         let mut last_error = None;
 
+        // Hashes of transactions we broadcast successfully but whose receipt we did not
+        // observe within the polling window. We keep them so that we can detect the case
+        // where one of those transactions was actually mined between our polling and the
+        // next retry attempt. Without this check we would re-query the nonce, see it has
+        // advanced (the original tx was mined), build a new tx with the incremented nonce,
+        // and that tx would revert on-chain because the operation was already completed.
+        let mut broadcast_hashes: Vec<H256> = Vec::new();
+
         for attempt in 0..max_attempts {
+            // Before sending a replacement tx, verify that none of the transactions we
+            // already broadcast have been confirmed in the meantime. If one was, we are
+            // done — there is no need to send more transactions.
+            for &hash in &broadcast_hashes {
+                match self
+                    .client
+                    .deref()
+                    .as_ref()
+                    .tx_receipt(hash)
+                    .await
+                {
+                    Ok(Some(receipt)) if receipt.status == Some(1.into()) => {
+                        tracing::info!(
+                            "Previously broadcast transaction {} was confirmed on retry check",
+                            hex::encode(hash)
+                        );
+                        return Ok(receipt.transaction_hash);
+                    }
+                    _ => {}
+                }
+            }
+
             let (base_fee_per_gas, priority_fee_per_gas) =
                 self.get_eth_fees(prev_base_fee_per_gas, prev_priority_fee_per_gas);
 
             let result = self
                 .send_tx(calldata.clone(), base_fee_per_gas, priority_fee_per_gas)
                 .await;
 
-            if let Err(err) = result {
-                tracing::info!(
-                    "Failed to send transaction, attempt {}, base_fee_per_gas {}, priority_fee_per_gas {}: {}",
-                    attempt,
-                    base_fee_per_gas,
-                    priority_fee_per_gas,
-                    err);
+            match result {
+                Ok(hash) => return Ok(hash),
+                Err((maybe_hash, err)) => {
+                    // If the tx was broadcast but the receipt polling timed out, save the
+                    // hash so we can check it at the top of the next iteration.
+                    if let Some(hash) = maybe_hash {
+                        broadcast_hashes.push(hash);
+                    }
+                    tracing::info!(
+                        "Failed to send transaction, attempt {}, base_fee_per_gas {}, priority_fee_per_gas {}: {}",
+                        attempt,
+                        base_fee_per_gas,
+                        priority_fee_per_gas,
+                        err
+                    );
+                    tokio::time::sleep(sleep_duration).await;
+                    prev_base_fee_per_gas = Some(base_fee_per_gas);
+                    prev_priority_fee_per_gas = Some(priority_fee_per_gas);
+                    last_error = Some(err);
+                }
+            }
+        }
 
-                tokio::time::sleep(sleep_duration).await;
-                prev_base_fee_per_gas = Some(base_fee_per_gas);
-                prev_priority_fee_per_gas = Some(priority_fee_per_gas);
-                last_error = Some(err)
-            } else {
-                return Ok(result.unwrap());
+        // Final pass: the last attempt may have broadcast a tx that was confirmed while
+        // we were about to give up.
+        for &hash in &broadcast_hashes {
+            match self
+                .client
+                .deref()
+                .as_ref()
+                .tx_receipt(hash)
+                .await
+            {
+                Ok(Some(receipt)) if receipt.status == Some(1.into()) => {
+                    tracing::info!(
+                        "Previously broadcast transaction {} was confirmed on final check",
+                        hex::encode(hash)
+                    );
+                    return Ok(receipt.transaction_hash);
+                }
+                _ => {}
             }
         }
 
@@ -154,19 +211,26 @@ impl ProofManagerClient {
             .into())
     }
 
+    /// Send a single transaction and wait for its receipt.
+    ///
+    /// Returns the confirmed transaction hash on success. On failure, returns a tuple of
+    /// `(Option<H256>, Error)`: the hash is `Some` when the transaction was broadcast to
+    /// the network but we timed out before seeing its receipt (so it may still be mined
+    /// later), and `None` when the transaction could not be sent at all.
     async fn send_tx(
         &self,
         calldata: Vec<u8>,
         base_fee_per_gas: u64,
         priority_fee_per_gas: u64,
-    ) -> anyhow::Result<H256> {
+    ) -> Result<H256, (Option<H256>, anyhow::Error)> {
         let nonce = self
             .client
             .deref()
             .as_ref()
             .nonce_at_for_account(self.client.sender_account(), BlockNumber::Latest)
             .await
-            .with_context(|| "failed getting transaction count")?
+            .with_context(|| "failed getting transaction count")
+            .map_err(|e| (None, e))?
             .as_u64();
 
         let options = Options {
@@ -181,16 +245,20 @@ impl ProofManagerClient {
             .client
             .sign_prepared_tx_for_addr(calldata, self.client.contract_addr(), options)
             .await
-            .context("cannot sign a transaction")?;
+            .context("cannot sign a transaction")
+            .map_err(|e| (None, e))?;
 
         let hash = self
             .client
             .deref()
             .as_ref()
             .send_raw_tx(signed_tx.raw_tx)
             .await
-            .context("failed sending transaction")?;
+            .context("failed sending transaction")
+            .map_err(|e| (None, e))?;
 
+        // From this point the tx is in the network. Any error we return must carry the
+        // hash so the caller can check whether the tx was eventually confirmed.
         let max_attempts = self.config.tx_receipt_checking_max_attempts;
         let sleep_duration = self.config.tx_receipt_checking_sleep;
         for _i in 0..max_attempts {
@@ -203,7 +271,8 @@ impl ProofManagerClient {
                 .context(format!(
                     "failed getting receipt for transaction {}",
                     hex::encode(hash)
-                ))?;
+                ))
+                .map_err(|e| (Some(hash), e))?;
             if let Some(receipt) = maybe_receipt {
                 tracing::info!("Transaction sent: {:?}", hex::encode(hash));
 
@@ -221,23 +290,33 @@ impl ProofManagerClient {
                     .context(format!(
                         "failed getting failure reason of transaction {}",
                         hex::encode(hash)
-                    ))?;
-
-                return Err(anyhow::Error::msg(format!(
-                    "Failed to send transaction {:?} failed with status {:?}, reason: {:?}",
-                    hex::encode(hash),
-                    receipt.status,
-                    reason
-                )));
+                    ))
+                    .map_err(|e| (Some(hash), e))?;
+
+                return Err((
+                    Some(hash),
+                    anyhow::Error::msg(format!(
+                        "Failed to send transaction {:?} failed with status {:?}, reason: {:?}",
+                        hex::encode(hash),
+                        receipt.status,
+                        reason
+                    )),
+                ));
             } else {
                 tokio::time::sleep(sleep_duration).await;
             }
         }
 
-        Err(anyhow::Error::msg(format!(
-            "Unable to retrieve transaction status in {} attempts",
-            max_attempts
-        )))
+        // The tx was broadcast but we could not confirm it within the polling window. Return
+        // the hash alongside the error so `send_tx_with_retries` can check it on the next
+        // iteration rather than blindly sending a new transaction.
+        Err((
+            Some(hash),
+            anyhow::Error::msg(format!(
+                "Unable to retrieve transaction status in {} attempts",
+                max_attempts
+            )),
+        ))
     }
 }
 
```

### core/node/eth_proof_manager/src/types.rs
```diff
@@ -14,12 +14,12 @@ pub enum ProvingNetwork {
 }
 
 impl ProvingNetwork {
-    pub fn from_u256(u: U256) -> Self {
+    pub fn from_u256(u: U256) -> anyhow::Result<Self> {
         match u.as_u32() {
-            0 => Self::None,
-            1 => Self::Fermah,
-            2 => Self::Lagrange,
-            _ => panic!("Invalid proving network: {}", u),
+            0 => Ok(Self::None),
+            1 => Ok(Self::Fermah),
+            2 => Ok(Self::Lagrange),
+            _ => anyhow::bail!("unknown proving network discriminant: {}", u),
         }
     }
 }
```

### core/node/eth_proof_manager/src/watcher/events/proof_request_acknowledged.rs
```diff
@@ -93,7 +93,8 @@ impl EventHandler for ProofRequestAcknowledgedHandler {
         };
 
         let assigned_to =
-            ProvingNetwork::from_u256(h256_to_u256(*log.topics.get(3).context("missing topic 3")?));
+            ProvingNetwork::from_u256(h256_to_u256(*log.topics.get(3).context("missing topic 3")?))
+                .context("invalid assigned_to in ProofRequestAcknowledged event")?;
 
         let event = ProofRequestAcknowledged {
             chain_id,
```

### core/node/eth_proof_manager/src/watcher/events/proof_request_proven.rs
```diff
@@ -1,4 +1,4 @@
-use std::sync::Arc;
+use std::{panic::AssertUnwindSafe, sync::Arc};
 
 use anyhow::Context;
 use async_trait::async_trait;
@@ -111,17 +111,20 @@ impl EventHandler for ProofRequestProvenHandler {
 
         let proof = match &decoded[0] {
             Token::Bytes(b) => b.clone(),
-            _ => panic!("Expected bytes"),
+            _ => anyhow::bail!("expected Bytes for proof field in ProofRequestProven event"),
         };
 
         let assigned_to = match &decoded[1] {
-            Token::Uint(u) => ProvingNetwork::from_u256(*u),
-            _ => panic!("Expected uint8"),
+            Token::Uint(u) => ProvingNetwork::from_u256(*u)
+                .context("invalid assigned_to in ProofRequestProven event")?,
+            _ => anyhow::bail!("expected Uint for assigned_to field in ProofRequestProven event"),
         };
 
         let requested_reward = match decoded[2] {
             Token::Uint(u) => u,
-            _ => panic!("Expected uint256"),
+            _ => anyhow::bail!(
+                "expected Uint for requested_reward field in ProofRequestProven event"
+            ),
         };
 
         let event = ProofRequestProven {
@@ -212,14 +215,28 @@ async fn verify_proof(
         .map_err(|e| anyhow::anyhow!("Failed to deserialize proof: {}", e))?;
 
     let verification_result = match proof.inner() {
-        TypedL1BatchProofForL1::Fflonk(proof) => {
-            let proof = proof.scheduler_proof;
-            fflonk::verify::<
-                _,
-                ZkSyncSnarkWrapperCircuitNoLookupCustomGate,
-                RollingKeccakTranscript<Fr>,
-            >(&verification_key, &proof, None)
-            .unwrap_or(false)
+        TypedL1BatchProofForL1::Fflonk(fflonk_proof) => {
+            let scheduler_proof = fflonk_proof.scheduler_proof;
+            // `fflonk::verify` can panic when given a structurally malformed proof
+            // (e.g. out-of-range field elements). Catching the panic here converts
+            // it into a regular `Err`, which the caller treats as an invalid proof
+            // and marks the batch accordingly — preventing a crash loop.
+            match std::panic::catch_unwind(AssertUnwindSafe(|| {
+                fflonk::verify::<
+                    _,
+                    ZkSyncSnarkWrapperCircuitNoLookupCustomGate,
+                    RollingKeccakTranscript<Fr>,
+                >(&verification_key, &scheduler_proof, None)
+                .unwrap_or(false)
+            })) {
+                Ok(result) => result,
+                Err(_) => {
+                    return Err(anyhow::anyhow!(
+                        "fflonk verifier panicked for batch {} — treating as invalid proof",
+                        batch_number
+                    ));
+                }
+            }
         }
         TypedL1BatchProofForL1::Plonk(_) => {
             return Err(anyhow::anyhow!(
```

### core/node/eth_proof_manager/src/watcher/mod.rs
```diff
@@ -69,8 +69,12 @@ impl EthProofWatcher {
     pub async fn run(&self, mut stop_receiver: watch::Receiver<bool>) -> anyhow::Result<()> {
         tracing::info!("Starting eth proof watcher");
 
-        let submitter_address: &'static str = self.client.submitter_address().to_string().leak();
-        let contract_address: &'static str = self.client.contract_address().to_string().leak();
+        // `Address` (`H160`) `Display` truncates to "0x1234…abcd". Use the alternate
+        // `LowerHex` formatter (`{:#x}`) to get the full 42-character address string.
+        let submitter_address: &'static str =
+            format!("{:#x}", self.client.submitter_address()).leak();
+        let contract_address: &'static str =
+            format!("{:#x}", self.client.contract_address()).leak();
 
         METRICS.submitter_address[&submitter_address].set(1);
         METRICS.contract_address[&contract_address].set(1);
```
