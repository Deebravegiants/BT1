### Title
`accept_requests` Flag Not Reset Across Resharing Transition Causes Signing Service Blackout - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `accept_requests` boolean flag, which gates all signature submission and response paths, can be set to `false` by `verify_tee()` when TEE validation fails in a way that would break the threshold relation. When participants subsequently call `vote_new_parameters()` to transition the contract into `Resharing` state, `accept_requests` is **not reset**. It remains `false` throughout the entire resharing period and persists as `false` after resharing completes and the contract returns to `Running` state. During this entire window, `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()` all fail with `TeeError::TeeValidationFailed`, making the signing service completely unavailable. This is the direct analog of the `hasSaleEnded()` misreport during a pause period: a lifecycle-gating flag is stale during an intermediate protocol state, and the mechanism to correct it (`verify_tee`) is unavailable during that state.

---

### Finding Description

**Root cause — `verify_tee` sets `accept_requests = false` and leaves it unrecovered across state transitions.**

`verify_tee()` is only callable in `Running` state: [1](#0-0) 

When `TeeValidationResult::Partial` is returned and the surviving participant set would violate the threshold relation, it sets: [2](#0-1) 

The contract stays in `Running` state. Participants can then call `vote_new_parameters()` to start a resharing to fix the participant set. However, `vote_new_parameters()` only updates `protocol_state` and never touches `accept_requests`: [3](#0-2) 

The `false` value is silently carried into `Resharing` state. During resharing, `verify_tee()` cannot be called to correct it — it panics on any non-`Running` state. When resharing completes via `vote_reshared()`, the transition back to `Running` also does not reset `accept_requests`: [4](#0-3) 

**Consequence — all signing paths are blocked.**

`check_request_preconditions()` (called by `sign`, `request_app_private_key`, `verify_foreign_transaction`) panics when `accept_requests` is `false`: [5](#0-4) 

`respond()` returns `TeeError::TeeValidationFailed` when `accept_requests` is `false`: [6](#0-5) 

The same guard appears in `respond_ckd()` and `respond_verify_foreign_tx()`: [7](#0-6) [8](#0-7) 

The `is_running_or_resharing()` check passes for `Resharing`, so the state-machine guard does not block these calls — only `accept_requests` does: [9](#0-8) 

---

### Impact Explanation

During the entire resharing period and after resharing completes, the MPC signing service is completely unavailable:

- No new `sign`, `request_app_private_key`, or `verify_foreign_transaction` calls can be accepted.
- No MPC node can submit a `respond`, `respond_ckd`, or `respond_verify_foreign_tx` call.
- All pending yield-resume promises for in-flight signature requests will time out and fail, causing the callers' transactions to revert.

This breaks the request-lifecycle invariant: `Resharing` is an active protocol phase (`is_running_or_resharing()` returns `true`) during which the contract is designed to continue serving responses, yet `accept_requests = false` silently overrides this. After resharing completes, the contract is in `Running` state with `accept_requests = false` — a permanently degraded state until `verify_tee()` is manually called again by a participant.

This maps to: **Medium — request-lifecycle and contract execution-flow manipulation that breaks production safety/accounting invariants.**

---

### Likelihood Explanation

The trigger sequence is realistic in production:

1. One or more participants' TEE attestations expire or reference a stale image hash.
2. A participant calls `verify_tee()`. The surviving valid-attestation set is below the threshold needed to safely kick out the invalid nodes, so `accept_requests = false` is set.
3. Participants decide to fix the cohort via `vote_new_parameters()` (adding replacement nodes or adjusting the threshold). This transitions to `Resharing` without resetting `accept_requests`.
4. The signing service is now dark for the entire resharing duration (potentially hours) and remains dark after resharing completes until `verify_tee()` is called again.

TEE certificate expiry is a scheduled, predictable event. The governance path (`vote_new_parameters` → resharing) is the standard remediation. No attacker action is required — the bug is triggered by normal operational events in a specific but realistic order.

---

### Recommendation

Reset `accept_requests = true` at the point where the contract transitions back to `Running` state after a successful resharing, inside `vote_reshared()`:

```rust
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = new_state;
+   self.accept_requests = true; // resharing completed with a new valid cohort
    self.recompute_available_foreign_chains();
    // ... cleanup promises
}
```

Alternatively, reset `accept_requests = true` when transitioning into `Resharing` via `vote_new_parameters()`, since the resharing itself is the remediation action. A defense-in-depth approach would also allow `verify_tee()` to be called during `Resharing` state so the flag can be corrected without waiting for resharing to complete.

---

### Proof of Concept

```
State: Running, accept_requests = true

1. TEE attestations for N participants expire.
2. Participant calls verify_tee():
   → TeeValidationResult::Partial, threshold relation broken
   → accept_requests = false
   → protocol_state stays Running

3. Participants call vote_new_parameters() (threshold votes reach quorum):
   → protocol_state = Resharing
   → accept_requests unchanged = false

4. During Resharing:
   - Any call to respond() → Err(TeeError::TeeValidationFailed)   [line 579-581]
   - Any call to sign()   → panic!(TeeError::TeeValidationFailed) [line 300-302]
   - verify_tee() → Err(InvalidState::ProtocolStateNotRunning)    [line 1697-1699]
   → Signing service completely unavailable

5. Resharing completes, vote_reshared() transitions to Running:
   → protocol_state = Running
   → accept_requests unchanged = false

6. Post-resharing Running state:
   - respond() still fails with TeeError::TeeValidationFailed
   - sign() still panics with TeeError::TeeValidationFailed
   → Signing service still completely unavailable

7. Only recovery: a participant manually calls verify_tee() again
   → If all new participants have valid attestations: accept_requests = true
```

### Citations

**File:** crates/contract/src/lib.rs (L300-302)
```rust
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

**File:** crates/contract/src/lib.rs (L661-663)
```rust

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
```

**File:** crates/contract/src/lib.rs (L711-713)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1170-1174)
```rust
        if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
            // Resharing has concluded, transition to running state
            self.protocol_state = new_state;
            self.recompute_available_foreign_chains();

```

**File:** crates/contract/src/lib.rs (L1697-1699)
```rust
        let ProtocolContractState::Running(running_state) = &mut self.protocol_state else {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        };
```

**File:** crates/contract/src/lib.rs (L1737-1738)
```rust
                    self.accept_requests = false;
                    return Ok(false);
```

**File:** crates/contract/src/lib.rs (L1910-1918)
```rust
            _ => {
                return Err(InvalidState::ProtocolStateNotRunning.into());
            }
        };

        self.tee_verifier_votes.retain(participants);

        Ok(())
    }
```

**File:** crates/contract/src/state.rs (L215-220)
```rust
    pub fn is_running_or_resharing(&self) -> bool {
        matches!(
            self,
            ProtocolContractState::Running(_) | ProtocolContractState::Resharing(_)
        )
    }
```
