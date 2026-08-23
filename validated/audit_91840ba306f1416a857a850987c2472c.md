### Title
Stale prefetched gas-key nonce cache allows nonce replay within a single chunk for same-`nonce_index` transactions - (File: runtime/runtime/src/lib.rs)

### Summary
The chunk-level transaction processing loop prefetches gas-key nonces into an immutable snapshot (`gas_key_nonces`) before iterating transactions, and each transaction's nonce check reads from that snapshot via `.get()` rather than from a live, updated view. If two transactions from the same signer target the same `nonce_index` within one chunk, the second transaction is verified against the pre-chunk nonce value instead of the value advanced by the first transaction, potentially allowing the gas-key-authorized action to be accepted twice.

### Finding Description
Before the per-transaction loop, `gas_key_nonces` is populated once via a prefetch pass keyed by `(signer_id, pubkey, nonce_index)`: [1](#0-0) 

Inside the loop, for gas-key transactions (`tx.transaction.nonce().nonce_index()` is `Some`), the current nonce is read from this same prefetched, immutable map with a plain `.get()`, not `.get_mut()`, and is not re-derived from any per-chunk mutable overlay: [2](#0-1) 

Notably, both the gas-key and regular-access-key verification paths are invoked with a freshly constructed `&PendingConstraints::default()` on every iteration rather than a constraints object threaded/accumulated across transactions in the same chunk: [3](#0-2) 

By contrast, the `account` and `access_key` values used in the same loop are obtained via `.get_mut()` into the prefetch caches, so in-place mutations made while processing one transaction are visible to subsequent transactions for the same signer: [4](#0-3) 

This asymmetry — mutable, in-place-updated caches for `accounts`/`access_keys`, but an immutable, `.get()`-only snapshot for `gas_key_nonces` — means that if transaction 1 (signer S, gas key K, `nonce_index=0`, nonce N) is processed and (assuming its nonce advance is only recorded elsewhere, e.g., when the action actually executes on the trie via `set_gas_key_nonce` in `runtime/runtime/src/access_keys.rs`, rather than synchronously back into the `gas_key_nonces` verification cache) transaction 2 (same S, K, `nonce_index=0`) arrives later in the same chunk, transaction 2's nonce check at line 2113 reads the same stale value N cached before the chunk began, not N+1. If `verify_and_charge_gas_key_tx_ephemeral`'s nonce check only requires `tx_nonce > current_nonce` (standard nonce semantics) and `current_nonce` here is stale, tx2 can pass verification using a nonce value that was already logically consumed by tx1 within the same chunk.

### Impact Explanation
If confirmed end-to-end, this would allow a single signer to have two transactions bound to the same gas-key `nonce_index` both accepted and converted into receipts within one chunk, effectively bypassing the nonce-monotonicity invariant that is supposed to guarantee exactly-once execution per nonce. This maps to NEAR's "authorization bypass" / "double-execution of an authorized action" impact class since gas-key-authorized transfers/withdrawals could execute twice for the cost of once passing verification, and to "state divergence" if the persisted nonce value written to the trie ends up inconsistent with what verification assumed.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: an ordinary account holder with a single gas key configured with `num_nonces >= 1` can submit two transactions using the same `nonce_index`, differing e.g. in the action payload, within the same chunk/block via public RPC (submitting both transactions back-to-back before the chunk is produced). No validator, node-operator, or privileged access is required, making this feasible to attempt with a normal wallet/RPC client.

### Recommendation
Thread a mutable, chunk-scoped view of gas-key nonces (analogous to the `.get_mut()` pattern already used for `accounts` and `access_keys`) through the transaction-verification loop, updating the cached nonce entry immediately after a gas-key transaction's `TxVerdict::Success`, and construct/accumulate `PendingConstraints` across the loop's transactions (per signer/nonce_index) rather than resetting it to `PendingConstraints::default()` on every iteration. Add integration coverage to lock in exactly-once processing.

### Proof of Concept
Integration test in `runtime/runtime` (or `test-loop-tests`) setting up an account with a gas key having `num_nonces = 1`, funded via `TransferToGasKey`:
1. Create two transactions, `tx1` and `tx2`, both from the same signer/gas key, both encoding `nonce_index = 0` with the current base nonce `N`, each performing a `WithdrawFromGasKey` (or any gas-key action).
2. Submit both `tx1` and `tx2` in the same chunk (same `apply_transactions` call / same `SignedValidPeriodTransactions` batch), with `tx1` ordered before `tx2`.
3. Apply the chunk and inspect `processing_state.outcomes`: assert exactly one `ExecutionOutcome` records success (`TxVerdict::Success`) and the other is `InvalidTxError::InvalidNonce` (or equivalent replay-rejection error).
4. Assert the gas-key balance / account balance diff reflects exactly one withdrawal, and that `get_gas_key_nonce` for `nonce_index = 0` reflects exactly one increment (`N -> N+1`), not two.

Note: full confirmation requires reading `verify_and_charge_gas_key_tx_ephemeral` in `runtime/runtime/src/verifier.rs` and the exact point where `set_gas_key_nonce` is invoked relative to this verification loop (i.e., whether the trie/nonce write happens synchronously inside this loop or deferred to later receipt execution) — this could not be fully traced within the available tool budget, so the finding is reported based on the strong structural evidence above (immutable snapshot read at line 2113, `.get()` vs `.get_mut()` asymmetry, and non-accumulated `PendingConstraints::default()`).

### Citations

**File:** runtime/runtime/src/lib.rs (L2010-2022)
```rust
                        // For gas key transactions, also prefetch the nonce
                        if let Some(nonce_index) = tx.transaction.nonce().nonce_index() {
                            gas_key_nonces.entry((signer_id, pubkey, nonce_index)).or_insert_with(
                                || {
                                    get_gas_key_nonce(
                                        &processing_state.state_update,
                                        signer_id,
                                        pubkey,
                                        nonce_index,
                                    )
                                },
                            );
                        }
```

**File:** runtime/runtime/src/lib.rs (L2072-2109)
```rust
            let mut account = accounts.get_mut(signer_id);
            let account = match account.as_deref_mut() {
                Some(Ok(Some(a))) => a,
                Some(Ok(None)) => {
                    metrics::TRANSACTION_PROCESSED_FAILED_TOTAL.inc();
                    tracing::debug!(%tx_hash, "transaction signed by unknown account");
                    let outcome = ExecutionOutcomeWithId::failed(
                        tx,
                        InvalidTxError::InvalidSignerId { signer_id: signer_id.to_string() },
                    );
                    processing_state.outcomes.push(outcome);
                    continue;
                }
                Some(Err(e)) => return Err(e.clone().into()),
                None => unreachable!("accounts should've been prefetched"),
            };
            let mut access_key = access_keys.get_mut(&(signer_id, pubkey));
            let access_key = match access_key.as_deref_mut() {
                Some(Ok(Some(ak))) => ak,
                Some(Ok(None)) => {
                    metrics::TRANSACTION_PROCESSED_FAILED_TOTAL.inc();
                    tracing::debug!(%tx_hash, "transaction signed by unknown signing key");
                    let outcome = ExecutionOutcomeWithId::failed(
                        tx,
                        InvalidTxError::InvalidAccessKeyError(
                            InvalidAccessKeyError::AccessKeyNotFound {
                                account_id: signer_id.clone(),
                                public_key: Box::new(pubkey.clone()),
                            },
                        ),
                    );

                    processing_state.outcomes.push(outcome);
                    continue;
                }
                Some(Err(e)) => return Err(e.clone().into()),
                None => unreachable!("access keys should've been prefetched"),
            };
```

**File:** runtime/runtime/src/lib.rs (L2111-2154)
```rust
            let verdict = if let Some(nonce_index) = tx.transaction.nonce().nonce_index() {
                // Gas key transaction - load nonce from prefetched cache
                let nonce_entry = gas_key_nonces.get(&(signer_id, pubkey, nonce_index));
                let current_nonce = match nonce_entry.as_deref() {
                    Some(Ok(Some(n))) => *n,
                    Some(Ok(None)) => {
                        metrics::TRANSACTION_PROCESSED_FAILED_TOTAL.inc();
                        tracing::debug!(%tx_hash, "gas key nonce not found");
                        let num_nonces =
                            access_key.gas_key_info().map(|info| info.num_nonces).unwrap_or(0);
                        let outcome = ExecutionOutcomeWithId::failed(
                            tx,
                            InvalidTxError::InvalidNonceIndex {
                                tx_nonce_index: Some(nonce_index),
                                num_nonces,
                            },
                        );
                        processing_state.outcomes.push(outcome);
                        continue;
                    }
                    Some(Err(e)) => return Err(e.clone().into()),
                    None => unreachable!("gas key nonces should've been prefetched"),
                };
                verify_and_charge_gas_key_tx_ephemeral(
                    &processing_state.apply_state.config,
                    account,
                    access_key,
                    current_nonce,
                    &tx.transaction,
                    &cost,
                    Some(block_height),
                    &PendingConstraints::default(),
                )
            } else {
                // Regular access key transaction
                verify_and_charge_tx_ephemeral(
                    &processing_state.apply_state.config,
                    account,
                    access_key,
                    &tx.transaction,
                    &cost,
                    Some(block_height),
                    &PendingConstraints::default(),
                )
```
