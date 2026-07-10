### Title
`verify_tee` Cannot Pause Signing During `Resharing` State — (`File: crates/contract/src/lib.rs`)

### Summary
The `verify_tee` function, which is the sole mechanism for setting `accept_requests = false` to halt signing when TEE security degrades, is hard-gated to the `Running` protocol state. During a `Resharing` epoch — which can be prolonged by node failures — TEE attestation expiry cannot trigger a signing halt, so the contract continues issuing threshold signatures without the TEE security invariant being enforced.

### Finding Description
The MPC contract uses a boolean flag `accept_requests` to gate all signing-related endpoints. When `verify_tee` detects that fewer than `threshold` participants hold valid TEE attestations, it sets `accept_requests = false`, blocking `sign`, `request_app_private_key`, `verify_foreign_transaction`, `respond`, `respond_ckd`, and `respond_verify_foreign_tx`.

However, `verify_tee` begins with a hard state guard:

```rust
let ProtocolContractState::Running(running_state) = &mut self.protocol_state else {
    return Err(InvalidState::ProtocolStateNotRunning.into());
};
``` [1](#0-0) 

This means `verify_tee` is entirely inoperable during `Resharing`. The only other places `accept_requests` is written are the two `init` constructors, both of which unconditionally set it to `true`. [2](#0-1) [3](#0-2) 

The `accept_requests` check in the three `respond*` functions and in `check_request_preconditions` is correct in isolation: [4](#0-3) [5](#0-4) 

But because `verify_tee` cannot write `accept_requests = false` while the protocol is in `Resharing`, the flag is permanently stuck at whatever value it held when resharing began. If TEE attestations expire for enough participants *during* resharing, no on-chain call can halt signing.

### Impact Explanation
The production safety invariant is that all signing nodes must hold valid TEE attestations before the contract issues threshold signatures. During a resharing epoch — which can last indefinitely if a node is killed or stalls, as demonstrated by the `test_request_during_resharing` e2e test — this invariant cannot be enforced. Signatures continue to be issued under the old key using the previous running state's participant set, even if those participants' TEE attestations have expired. This breaks the contract's TEE-enforcement guarantee and allows signatures to be produced without the required hardware-level security assurance.

**Impact class**: Medium — contract execution-flow manipulation that breaks a production safety/accounting invariant (`accept_requests` cannot be set to `false` during `Resharing`).

### Likelihood Explanation
Resharing is triggered by `vote_new_parameters` or automatically by `verify_tee` when a partial kickout is possible. Resharing can be prolonged by node failures (a node being killed blocks completion). TEE attestations have a configurable expiry (`tee_upgrade_deadline_duration_seconds`). If attestations expire during a stalled resharing, the window where `verify_tee` is inoperable coincides exactly with the window where attestation expiry matters most. This is a realistic operational scenario, not a theoretical one. [6](#0-5) 

### Recommendation
Extend `verify_tee` to handle the `Resharing` state by evaluating TEE attestation validity against the **previous running state's** participant set (which is the set currently performing signing). If attestations are degraded below threshold during resharing, set `accept_requests = false`. Alternatively, extract the `accept_requests = false` write path into a separate, state-agnostic function callable by participants in any non-`NotInitialized` state.

### Proof of Concept

1. Contract is `Running` with `accept_requests = true` and valid TEE attestations for all participants.
2. `vote_new_parameters` is called by threshold participants → contract transitions to `Resharing`.
3. One node is killed → resharing stalls indefinitely (as in `test_request_during_resharing`).
4. TEE attestations for enough participants expire (past `tee_upgrade_deadline_duration_seconds`).
5. An operator calls `verify_tee` → returns `Err(ProtocolStateNotRunning)` — no effect on `accept_requests`.
6. `sign` is called by a user → `check_request_preconditions` passes (`accept_requests` is still `true`, `domain_registry()` succeeds for `Resharing` via `previous_running_state.domains`).
7. Nodes call `respond` → `accept_requests` check passes → signature is delivered.

The contract has issued a threshold signature without the TEE invariant being met, with no on-chain mechanism available to prevent it. [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** crates/contract/src/lib.rs (L1693-1699)
```rust
    pub fn verify_tee(&mut self) -> Result<bool, Error> {
        log!("verify_tee: signer={}", env::signer_account_id());
        // Caller must be a participant (node or operator).
        self.voter_or_panic();
        let ProtocolContractState::Running(running_state) = &mut self.protocol_state else {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        };
```

**File:** crates/contract/src/lib.rs (L1702-1708)
```rust
        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        match self.tee_state.reverify_and_cleanup_participants(
            current_params.participants(),
            tee_upgrade_deadline_duration,
        ) {
```

**File:** crates/contract/src/lib.rs (L1962-1962)
```rust
            accept_requests: true,
```

**File:** crates/contract/src/lib.rs (L2041-2041)
```rust
            accept_requests: true,
```

**File:** crates/contract/src/state.rs (L34-41)
```rust
    pub fn domain_registry(&self) -> Result<&DomainRegistry, Error> {
        let domain_registry = match self {
            ProtocolContractState::Running(state) => &state.domains,
            ProtocolContractState::Resharing(state) => &state.previous_running_state.domains,
            _ => return Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
        };

        Ok(domain_registry)
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
