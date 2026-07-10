### Title
Missing `recompute_available_foreign_chains()` call in `vote_cancel_resharing()` leaves foreign-chain availability cache stale — (File: `crates/contract/src/lib.rs`)

---

### Summary

`vote_cancel_resharing()` transitions the contract back to the previous `RunningContractState` but omits the `recompute_available_foreign_chains()` call that `vote_reshared()` correctly makes after every Running-state transition. This leaves the foreign-chain availability cache reflecting the prospective (cancelled) participant set rather than the restored one, allowing `verify_foreign_transaction()` to accept requests for chains the restored participant set cannot service.

---

### Finding Description

When resharing completes successfully, `vote_reshared()` transitions to `Running` and immediately calls `recompute_available_foreign_chains()`:

```rust
// crates/contract/src/lib.rs  ~line 1170
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = new_state;
    self.recompute_available_foreign_chains();   // ← present
    // … cleanup promises …
}
```

When resharing is *cancelled*, `vote_cancel_resharing()` transitions back to the previous `RunningContractState` but **omits** the same call:

```rust
// crates/contract/src/lib.rs  ~line 1258
if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
    self.protocol_state = new_state;
    // ← recompute_available_foreign_chains() is missing
}
```

During resharing, prospective participants are permitted to call `register_foreign_chains_config()`, which internally calls `recompute_available_foreign_chains()` and updates the cache to include foreign chains supported by those new nodes. When resharing is subsequently cancelled, the contract reverts to the old participant set, but the cache still reflects the new participants' supported chains.

`verify_foreign_transaction()` gates acceptance on `get_supported_foreign_chains()`, which reads from this cache:

```rust
// crates/contract/src/lib.rs  ~line 533
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) {
    env::panic_str(…);
}
```

With a stale cache, the contract accepts requests for chains that the restored (old) participant set cannot actually service.

`recompute_available_foreign_chains()` itself is correct: it derives the active TLS-key set from the *current* `threshold_parameters()` and passes it to `update_available_chains_config_cache`:

```rust
// crates/contract/src/lib.rs  ~line 1047
let active_tls_keys: BTreeSet<_> = params
    .participants()
    .participants()
    .iter()
    .map(|(_, _, info)| info.tls_public_key.clone())
    .collect();
self.foreign_chains
    .get_mut()
    .update_available_chains_config_cache(&active_tls_keys, threshold);
```

After `vote_cancel_resharing()` restores the old participant set, calling this function would correctly evict the new participants' chains from the cache. The omission means it is never called.

---

### Impact Explanation

After resharing cancellation, the stale cache may list foreign chains as "available" that the restored participant set cannot service. An unprivileged user can call `verify_foreign_transaction()` for such a chain; the contract accepts the request and creates a yield-resume promise. The MPC nodes cannot complete the verification (fewer than threshold old participants support that chain), leaving the request permanently stuck and the user's deposit consumed. This breaks the request-lifecycle safety invariant: **Medium — request-lifecycle manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration.**

---

### Likelihood Explanation

Resharing is a routine governance operation. Prospective participants commonly register foreign chain support during resharing (they are permitted to do so via `register_foreign_chains_config()`, which is callable by any existing-or-prospective participant). Resharing cancellation requires only a threshold of old-participant votes — a realistic governance outcome when the new cohort fails to come online. After cancellation, any unprivileged user can trigger the stale-cache path by submitting a `verify_foreign_transaction()` request for a chain supported only by the cancelled new participants.

---

### Recommendation

Add a call to `recompute_available_foreign_chains()` in `vote_cancel_resharing()` after the state transition, mirroring the pattern in `vote_reshared()`:

```diff
 pub fn vote_cancel_resharing(&mut self) -> Result<(), Error> {
     Self::assert_caller_is_signer();
     log!("vote_cancel_resharing: signer={}", env::signer_account_id());

     if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
         self.protocol_state = new_state;
+        self.recompute_available_foreign_chains();
     }

     Ok(())
 }
```

---

### Proof of Concept

1. Contract is in `Running` state; old participants support chains A and B only.
2. Governance votes to reshare with a new cohort that additionally supports chain C.
3. New participants call `register_foreign_chains_config()` → `recompute_available_foreign_chains()` updates the cache to include chain C.
4. Old participants cast threshold votes to cancel resharing → `vote_cancel_resharing()` restores the old `RunningContractState` **without** calling `recompute_available_foreign_chains()`.
5. Cache still lists chain C as available.
6. Unprivileged user calls `verify_foreign_transaction()` for chain C with the minimum 1 yoctoNEAR deposit.
7. Contract accepts the request (cache says chain C is supported) and enqueues a yield-resume promise.
8. MPC nodes cannot complete verification (old participants do not support chain C).
9. The yield-resume promise never resolves; the request is permanently stuck and the user's deposit is consumed.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L533-542)
```rust
        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }
```

**File:** crates/contract/src/lib.rs (L1028-1056)
```rust
    fn recompute_available_foreign_chains(&mut self) {
        let Ok(params) = self.protocol_state.threshold_parameters() else {
            return;
        };
        // TODO(#3556): replace this with a per-scheme
        // `required_active_signers(protocol, reconstruction_threshold)`.
        let Some(threshold) = self.protocol_state.domain_registry().ok().and_then(|r| {
            r.domains()
                .iter()
                .filter(|d| d.purpose == DomainPurpose::ForeignTx)
                .map(|d| d.reconstruction_threshold.inner())
                .max()
        }) else {
            // No op if contract isn't in Running or Resharing state, or
            // there is no foreign tx domain registered.
            // Not panicking is intentional.
            log!("Skipping available foreign chains recomputation");
            return;
        };
        let active_tls_keys: BTreeSet<_> = params
            .participants()
            .participants()
            .iter()
            .map(|(_, _, info)| info.tls_public_key.clone())
            .collect();
        self.foreign_chains
            .get_mut()
            .update_available_chains_config_cache(&active_tls_keys, threshold);
    }
```

**File:** crates/contract/src/lib.rs (L1161-1173)
```rust
    pub fn vote_reshared(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_reshared: signer={}, resharing_id={:?}",
            env::signer_account_id(),
            key_event_id,
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
            // Resharing has concluded, transition to running state
            self.protocol_state = new_state;
            self.recompute_available_foreign_chains();
```

**File:** crates/contract/src/lib.rs (L1254-1263)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_resharing: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
            self.protocol_state = new_state;
        }

        Ok(())
    }
```
