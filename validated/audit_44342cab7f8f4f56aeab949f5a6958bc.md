### Title
`verify_tee()` Setting `accept_requests = false` Permanently Strands Already-Queued Sign/CKD Requests — (File: `crates/contract/src/lib.rs`)

---

### Summary

When `verify_tee()` sets `accept_requests = false` because kicking out participants with expired TEE attestations would break the threshold relation, it simultaneously blocks `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()` from fulfilling **already-queued** yield-resume requests. Those in-flight requests will time out and fail. Users who submitted valid sign requests before the flag was set have no mechanism to avoid this outcome — the exact structural analog to the AuraLocker-shutdown penalty trap.

---

### Finding Description

`verify_tee()` is callable by any single participant (voter). When fewer than `threshold` participants have valid TEE attestations and kicking them out would violate the threshold relation, the function sets `self.accept_requests = false` and returns `Ok(false)`:

```rust
// crates/contract/src/lib.rs  ~L1737
self.accept_requests = false;
return Ok(false);
```

The docstring explicitly states the intent: *"stops the contract from accepting new signature requests **or responses**."*

All three node-facing response methods enforce this flag:

```rust
// respond()  L579-581
if !self.accept_requests {
    return Err(TeeError::TeeValidationFailed.into());
}

// respond_ckd()  L662-664
if !self.accept_requests {
    return Err(TeeError::TeeValidationFailed.into());
}

// respond_verify_foreign_tx()  L711-713
if !self.accept_requests {
    return Err(TeeError::TeeValidationFailed.into());
}
```

Meanwhile, `sign()`, `request_app_private_key()`, and `verify_foreign_transaction()` use `check_request_preconditions()`, which also gates on `accept_requests`:

```rust
// L300-302
if !self.accept_requests {
    env::panic_str(&TeeError::TeeValidationFailed.to_string())
}
```

The result is a two-sided lockout:

1. **New requests** are rejected at submission time — users receive an immediate error and lose only gas.
2. **Already-queued requests** (submitted before the flag was set) are silently stranded: nodes cannot call `respond*()` to fulfill them, so the NEAR runtime's ~200-block yield-timeout fires, the yield-callback (`return_signature_and_clean_state_on_success`) pops the slot and schedules `fail_on_timeout`, and the original caller's transaction fails.

Users in category 2 have **no recourse**: they cannot cancel the yield, cannot retry, and cannot force a response. The only path — waiting for `verify_tee()` to succeed again and `accept_requests` to be restored — does not resurrect timed-out yields; those are permanently gone.

---

### Impact Explanation

**Medium — request-lifecycle invariant broken without operator misconfiguration.**

The production invariant is: a request accepted by `sign()` (deposit paid, yield created, entry stored in `pending_signature_requests`) will eventually be either fulfilled by `respond()` or explicitly timed out by the runtime. The `accept_requests = false` path breaks the fulfillment half of this invariant for all in-flight requests at the moment the flag is set. Concretely:

- Users lose attached gas and the 1-yoctoNEAR deposit.
- Time-sensitive cross-chain operations (bridge unlocks, atomic swaps) that depend on the signature fail on the foreign chain, potentially causing indirect fund loss.
- The pending-request map entries are cleaned up by the timeout callback, so no storage is permanently leaked, but the user-visible outcome is an unrecoverable failed transaction.

This matches: *"request-lifecycle … manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."*

---

### Likelihood Explanation

- TEE attestations expire on a 7-day default deadline (`DEFAULT_TEE_UPGRADE_DEADLINE_DURATION_SECONDS`). Expiry is a routine operational event, not an attack prerequisite.
- `verify_tee()` requires only a single participant (voter) to call it — no threshold collusion needed.
- A Byzantine participant strictly below the signing threshold can call `verify_tee()` at any moment when one or more peer attestations have expired and the surviving valid set is below threshold. This triggers `accept_requests = false` and strands every concurrently pending request.
- The window of in-flight requests is always non-zero on a live network; the attack is repeatable whenever attestations lapse.

---

### Recommendation

Decouple the "accept new requests" gate from the "allow nodes to respond to already-accepted requests" gate. Specifically:

1. **Do not check `accept_requests` inside `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()`.** Those methods already authenticate the caller as an attested participant and verify the protocol is Running-or-Resharing; that is sufficient to guard against unauthorized responses.
2. Alternatively, when `accept_requests` transitions to `false`, immediately drain all pending yield queues with an explicit error via `promise_yield_resume`, so users receive a fast, deterministic failure rather than waiting for the ~200-block timeout.

---

### Proof of Concept

1. User calls `sign(request)` with 1 yoctoNEAR deposit → `check_request_preconditions` passes (`accept_requests == true`) → yield created, entry stored in `pending_signature_requests`.
2. One participant's TEE attestation expires. A second participant (Byzantine, below threshold) calls `verify_tee()`. The surviving valid set is below threshold, so `accept_requests = false` is set.
3. MPC nodes attempt `respond(request, signature)` → blocked at `if !self.accept_requests { return Err(TeeError::TeeValidationFailed) }`.
4. ~200 blocks elapse. The NEAR runtime fires `return_signature_and_clean_state_on_success(request, Err(PromiseError::Failed))` → `pop_oldest_pending_yield` removes the slot → `fail_on_timeout` is scheduled → user's original `sign()` transaction resolves as failed.
5. User has lost gas, lost the deposit, and received no signature. Even after `verify_tee()` eventually returns `true` and `accept_requests` is restored, the timed-out yield cannot be recovered.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L579-581)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L662-664)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L711-713)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1737-1738)
```rust
                    self.accept_requests = false;
                    return Ok(false);
```

**File:** crates/contract/src/lib.rs (L2254-2271)
```rust
        match signature {
            Ok(signature) => PromiseOrValue::Value(signature),
            Err(_) => {
                pending_requests::pop_oldest_pending_yield(
                    &mut self.pending_signature_requests,
                    &request,
                );

                let fail_on_timeout_gas = Gas::from_tgas(self.config.fail_on_timeout_tera_gas);
                let promise = Promise::new(env::current_account_id()).function_call(
                    method_names::FAIL_ON_TIMEOUT.to_string(),
                    vec![],
                    NearToken::from_near(0),
                    fail_on_timeout_gas,
                );
                near_sdk::PromiseOrValue::Promise(promise.as_return())
            }
        }
```

**File:** crates/contract/src/pending_requests.rs (L97-111)
```rust
pub(crate) fn pop_oldest_pending_yield<K>(requests: &mut LookupMap<K, Vec<YieldIndex>>, request: &K)
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let Some(queue) = requests.get_mut(request) else {
        return;
    };
    if queue.is_empty() {
        requests.remove(request);
        return;
    }
    queue.remove(0);
    if queue.is_empty() {
        requests.remove(request);
    }
```
