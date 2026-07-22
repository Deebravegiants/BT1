### Title
Gateway Proof Verification Executes Before Balance Check, Enabling Free CPU-Exhaustion DOS via Invalid Client-Side Proofs - (File: `crates/apollo_gateway/src/gateway.rs`)

---

### Summary

The gateway's `add_tx_inner` function runs CPU-intensive ZK proof verification **before** the stateful balance check. An attacker can submit many Invoke V3 transactions with syntactically valid `proof_facts` but cryptographically invalid `proof` bytes, triggering expensive circuit verification for each, while paying zero fees because the balance check never executes.

---

### Finding Description

In `add_tx_inner`, the execution order is:

1. **Stateless validation** — checks proof/proof_facts consistency, non-zero resource bounds, proof size limit.
2. **`convert_rpc_tx_to_internal_and_executable_txs`** — spawns and immediately awaits proof verification via `spawn_proof_verification` → `run_proof_verification` → `privacy_circuit_verify_v1::verify_recursive_circuit` (CPU-intensive).
3. **Stateful validation** — checks account balance, nonce, and detailed proof_facts structure. [1](#0-0) 

If the proof is cryptographically invalid, step 2 returns an error and step 3 (the balance check) **never executes**.

The stateless validator only requires:
- Both `proof_facts` and `proof` are non-empty (consistency check).
- Proof size ≤ `max_proof_size` (480,000 bytes).
- At least one resource bound is non-zero (no balance check). [2](#0-1) [3](#0-2) 

The CPU-intensive circuit verifier is reached as long as:
- `proof` is non-empty.
- `proof_facts[0]` equals the V1 version marker (a public constant).
- `proof_facts.len() >= 3`. [4](#0-3) 

The balance check (`verify_can_pay_committed_bounds`) lives inside `perform_pre_validation_stage`, which is only reached during stateful validation — **after** proof verification has already run and failed. [5](#0-4) 

The `contains_proof` short-circuit in `run_proof_verification` does not help: the attacker uses a fresh, unique `proof_facts` value per request (different random bytes → different Poseidon hash), so the cache is always missed. [6](#0-5) 

---

### Impact Explanation

An attacker with **zero on-chain balance** can flood the gateway with Invoke V3 transactions that each trigger a full `verify_recursive_circuit` call. Because the balance check is never reached, there is no economic cost per attempt. The gateway's CPU is consumed verifying invalid proofs, starving legitimate transactions of processing capacity. This maps to:

> **High. Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing.**

---

### Likelihood Explanation

The attack requires only:
1. Knowledge of the V1 proof version marker (a public constant in the codebase).
2. The ability to POST to the gateway's HTTP endpoint.
3. Zero on-chain balance.

No privileged access, no existing funds, and no cryptographic capability are needed. The attacker constructs `proof_facts = [V1_MARKER, VIRTUAL_SNOS, <any_felt>, ...]` and `proof = <random bytes>`, both of which pass all stateless checks.

---

### Recommendation

Perform a lightweight balance pre-check (or at minimum a nonce/existence check) **before** spawning the proof verification task. Concretely, reorder `add_tx_inner` so that `extract_state_nonce_and_run_validations` (which calls `verify_can_pay_committed_bounds`) executes before `convert_rpc_tx_to_internal_and_executable_txs`. Alternatively, add a dedicated stateless balance-existence check (e.g., reject if the account's fee-token balance is zero) as a cheap pre-filter before the expensive circuit call.

---

### Proof of Concept

```
# 1. Craft a minimal valid-looking proof_facts (V1 marker + VIRTUAL_SNOS + padding)
proof_facts = [
    0x50524f4f4631,          # PROOF_VERSION_V1 (public constant)
    0x5649525455414c5f534e4f53,  # VIRTUAL_SNOS (public constant)
    0xdeadbeef,              # arbitrary program_hash
    0x1, 0x2, 0x3            # arbitrary padding
]

# 2. Craft an invalid proof (random bytes, non-empty, within 480 KB limit)
proof = base64_encode(random_bytes(1024))

# 3. Submit Invoke V3 with non-zero resource bounds but zero account balance
POST /gateway/add_transaction {
  "type": "INVOKE",
  "version": "0x3",
  "resource_bounds": { "l2_gas": { "max_amount": "0x1", "max_price_per_unit": "0x1" }, ... },
  "proof_facts": proof_facts,
  "proof": proof,
  ...
}

# 4. Repeat with fresh proof_facts (different random bytes) to bypass contains_proof cache.
# Each request triggers verify_recursive_circuit before any balance check.
# The attacker's account balance is never read.
``` [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_gateway/src/gateway.rs (L214-298)
```rust
    async fn add_tx_inner(
        &self,
        tx: RpcTransaction,
        p2p_message_metadata: Option<BroadcastedMessageMetadata>,
    ) -> GatewayResult<GatewayOutput> {
        let mut metric_counters = GatewayMetricHandle::new(&tx, &p2p_message_metadata);
        metric_counters.count_transaction_received();
        if let RpcTransaction::Invoke(RpcInvokeTransaction::V3(ref inv)) = tx {
            if !inv.proof_facts.is_empty() {
                metric_counters.count_private_transaction_received();
            }
        }
        let is_p2p = p2p_message_metadata.is_some();

        if let RpcTransaction::Declare(ref declare_tx) = tx {
            if let Err(e) = self.check_declare_permissions(declare_tx) {
                metric_counters.record_add_tx_failure(&e);
                return Err(e);
            }
        }

        // Perform stateless validations.
        self.stateless_tx_validator.validate(&tx)?;

        let tx_signature = tx.signature().clone();

        // Declare conversions overload the compiler component's CPU and memory. Reject declares if
        // there are too many declares compiling in parallel. The permit is held only across
        // compilation and released before stateful validation.
        let compilation_permit = if matches!(tx, RpcTransaction::Declare(_)) {
            Some(self.declare_compilation_semaphore.try_acquire().map_err(|_| {
                let error = StarknetError::too_many_concurrent_declare_compilations();
                metric_counters.record_add_tx_failure(&error);
                error
            })?)
        } else {
            None
        };

        let (internal_tx, executable_tx, proof_data) =
            self.convert_rpc_tx_to_internal_and_executable_txs(tx, &tx_signature).await?;
        drop(compilation_permit);

        let mut stateful_transaction_validator = self
            .stateful_tx_validator_factory
            .instantiate_validator(self.config.dynamic_config.native_classes_whitelist.clone())
            .await
            .inspect_err(|e| metric_counters.record_add_tx_failure(e))?;

        let nonce = stateful_transaction_validator
            .extract_state_nonce_and_run_validations(&executable_tx, self.mempool_client.clone())
            .await
            .inspect_err(|e| metric_counters.record_add_tx_failure(e))?;

        let proof_archive_handle = self
            .store_proof_and_spawn_archiving(proof_data, internal_tx.tx_hash, is_p2p)
            .await
            .inspect_err(|e| metric_counters.record_add_tx_failure(e))?;

        let gateway_output = create_gateway_output(&internal_tx);

        let add_tx_args = AddTransactionArgsWrapper {
            args: AddTransactionArgs::new(internal_tx, nonce),
            p2p_message_metadata,
        };

        // Await as late as possible for proof archiving before sending the transaction to the
        // mempool.
        Self::await_proof_archiving(proof_archive_handle)
            .await
            .inspect_err(|e| metric_counters.record_add_tx_failure(e))?;

        let mempool_client_result = self.mempool_client.add_tx(add_tx_args).await;
        match mempool_client_result_to_deprecated_gw_result(&tx_signature, mempool_client_result) {
            Ok(()) => {}
            Err(e) => {
                metric_counters.record_add_tx_failure(&e);
                return Err(e);
            }
        };

        metric_counters.transaction_sent_to_mempool();

        Ok(gateway_output)
    }
```

**File:** crates/apollo_gateway/src/stateless_transaction_validator.rs (L56-88)
```rust
    fn validate_resource_bounds(
        &self,
        tx: &RpcTransaction,
    ) -> StatelessTransactionValidatorResult<()> {
        if !self.config.validate_resource_bounds {
            return Ok(());
        }

        let resource_bounds = *tx.resource_bounds();
        // The resource bounds should be positive even without the tip.
        if ValidResourceBounds::AllResources(resource_bounds).max_possible_fee(Tip::ZERO) == Fee(0)
        {
            return Err(StatelessTransactionValidatorError::ZeroResourceBounds { resource_bounds });
        }

        if resource_bounds.l2_gas.max_price_per_unit.0 < self.config.min_gas_price {
            return Err(StatelessTransactionValidatorError::MaxGasPriceTooLow {
                gas_price: resource_bounds.l2_gas.max_price_per_unit,
                min_gas_price: self.config.min_gas_price,
            });
        }

        // TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.
        if let RpcTransaction::Declare(_) = tx {
        } else if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
            return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
                gas_amount: resource_bounds.l2_gas.max_amount,
                max_gas_amount: self.config.max_l2_gas_amount,
            });
        }

        Ok(())
    }
```

**File:** crates/apollo_gateway/src/stateless_transaction_validator.rs (L249-263)
```rust
    fn validate_proof_facts_and_proof_consistency(
        &self,
        tx: &RpcInvokeTransaction,
    ) -> StatelessTransactionValidatorResult<()> {
        let RpcInvokeTransaction::V3(tx) = tx;
        let has_proof_facts = !tx.proof_facts.is_empty();
        let has_proof = !tx.proof.is_empty();
        if has_proof_facts != has_proof {
            return Err(StatelessTransactionValidatorError::ProofFactsAndProofConsistency {
                has_proof_facts,
                has_proof,
            });
        }
        Ok(())
    }
```

**File:** crates/starknet_proof_verifier/src/proof_verifier.rs (L126-157)
```rust
pub fn verify_proof(proof_facts: ProofFacts, proof: Proof) -> Result<(), VerifyProofError> {
    // Reject empty proof payloads before running the verifier.
    if proof.is_empty() {
        return Err(VerifyProofError::EmptyProof);
    }

    let proof_version_felt = proof_facts.0.first().copied().unwrap_or_default();
    let proof_version = ProofVersion::try_from(proof_version_felt)
        .map_err(|()| VerifyProofError::InvalidProofVersion { actual: proof_version_felt })?;

    let output_preimage = reconstruct_output_preimage(&proof_facts)?;
    // TODO(Avi): Avoid cloning the proof.
    let proof_bytes = proof.0.to_vec();

    match proof_version {
        // V0 proofs are no longer verifiable: the v0 circuit was removed. V0 proof facts are only
        // tolerated by the blockifier (gated per protocol version) for replaying historical blocks.
        ProofVersion::V0 => {
            return Err(VerifyProofError::InvalidProofVersion { actual: proof_version_felt });
        }
        ProofVersion::V1 => {
            let proof_output = privacy_circuit_verify_v1::PrivacyProofOutput {
                proof: proof_bytes,
                output_preimage,
            };
            privacy_circuit_verify_v1::verify_recursive_circuit(&proof_output)
                .map_err(|e| VerifyProofError::Verification(e.to_string()))?;
        }
    }

    Ok(())
}
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L355-372)
```rust
    pub fn perform_pre_validation_stage<S: State + StateReader>(
        &self,
        state: &mut S,
        tx_context: &TransactionContext,
    ) -> TransactionPreValidationResult<()> {
        let tx_info = &tx_context.tx_info;
        Self::handle_nonce(state, tx_info, self.execution_flags.strict_nonce_check)?;

        if self.execution_flags.charge_fee {
            self.check_fee_bounds(tx_context)?;

            verify_can_pay_committed_bounds(state, tx_context).map_err(Box::new)?;
        }

        self.validate_proof_facts(&tx_context.block_context, state)?;

        Ok(())
    }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L398-424)
```rust
    async fn run_proof_verification(
        proof_facts: ProofFacts,
        proof: Proof,
        proof_manager_client: SharedProofManagerClient,
    ) -> Result<bool, TransactionConverterError> {
        let contains_proof = proof_manager_client.contains_proof(proof_facts.clone()).await?;

        if contains_proof {
            return Ok(false);
        }

        let proof_facts_hash = proof_facts.hash();
        let verify_start = Instant::now();
        tokio::task::spawn_blocking(move || {
            starknet_proof_verifier::verify_proof(proof_facts, proof)
        })
        .await
        .expect("proof verification task panicked")?;
        let verify_duration = verify_start.elapsed();
        PROOF_VERIFICATION_LATENCY.record(verify_duration.as_secs_f64());
        info!(
            "Proof verification took: {verify_duration:?} for proof facts hash: \
             {proof_facts_hash:?}"
        );

        Ok(true)
    }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L428-441)
```rust
    fn spawn_proof_verification(
        &self,
        proof_facts: ProofFacts,
        proof: Proof,
    ) -> TransactionConverterResult<VerificationHandle> {
        let pmc = self.proof_manager_client.clone();
        let task_proof_facts = proof_facts.clone();
        let task_proof = proof.clone();
        let verification_task = tokio::spawn(async move {
            Self::run_proof_verification(task_proof_facts, task_proof, pmc).await?;
            Ok(())
        });
        Ok(VerificationHandle { proof_facts, proof, verification_task })
    }
```
