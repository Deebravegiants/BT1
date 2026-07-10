### Title
`Initializing` State Blocks All Signing Operations Across All Existing Domains — (`File: crates/contract/src/state.rs`)

---

### Summary

When the MPC contract transitions to the `Initializing` state (triggered by `vote_add_domains`), every user-facing request — `sign`, `request_app_private_key`, and `verify_foreign_transaction` — is unconditionally blocked for **all** existing domains, including those whose keys are already fully generated and operational. A Byzantine participant strictly below the signing threshold can deliberately stall key generation, holding the contract in `Initializing` state and freezing all signing service for an indefinite period.

---

### Finding Description

`domain_registry()` in `state.rs` returns an error for the `Initializing` state:

```rust
pub fn domain_registry(&self) -> Result<&DomainRegistry, Error> {
    let domain_registry = match self {
        ProtocolContractState::Running(state) => &state.domains,
        ProtocolContractState::Resharing(state) => &state.previous_running_state.domains,
        _ => return Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
    };
    Ok(domain_registry)
}
``` [1](#0-0) 

`check_request_preconditions`, called by every user-facing method, immediately panics on that error:

```rust
let domains = match self.protocol_state.domain_registry() {
    Ok(domains) => domains,
    Err(err) => env::panic_str(&err.to_string()),
};
``` [2](#0-1) 

This panic path is reached by `sign`, `request_app_private_key`, and `verify_foreign_transaction` — every user-facing signing entry point: [3](#0-2) 

The `Initializing` state is entered when all participants unanimously vote via `vote_add_domains`. The `InitializingContractState` struct already carries `generated_keys` — the fully-operational keys for all pre-existing domains — but the contract makes no use of them for signing during this phase: [4](#0-3) 

The `vote_add_domains` transition in `running.rs` requires every participant to vote (unanimous, not merely threshold):

```rust
if self.parameters.participants().len() as u64 == n_votes {
``` [5](#0-4) 

Once in `Initializing`, a Byzantine participant below the signing threshold can deliberately stay offline, stalling the distributed key generation. The only recovery path is `vote_cancel_keygen`, which itself requires a threshold quorum to organize: [6](#0-5) 

---

### Impact Explanation

All pending and incoming signature requests — across every existing, fully-keyed domain — are rejected with `ProtocolStateNotRunningNorResharing` for the entire duration the contract remains in `Initializing`. This freezes the signing service for all users of the MPC network. Because `generated_keys` for pre-existing domains are present in the `Initializing` state but never consulted, the freeze is structurally unnecessary: existing domains could continue to serve signing requests while the new domain's key is being generated. The impact maps to **Medium** — request-lifecycle and contract execution-flow manipulation that breaks the production safety invariant that existing, fully-operational domains remain available.

---

### Likelihood Explanation

The trigger (`vote_add_domains` reaching unanimous vote) is a routine governance operation expected to occur whenever the network expands its signing capabilities. Once the contract enters `Initializing`, a single Byzantine participant strictly below the signing threshold can extend the freeze indefinitely by refusing to participate in key generation. The remaining honest participants must then coordinate a `vote_cancel_keygen` quorum — a non-trivial operational step — before signing resumes. The window of unavailability is therefore attacker-controlled and unbounded.

---

### Recommendation

`domain_registry()` should return the registry of **already-generated** domains when in `Initializing` state, rather than returning an error. The `InitializingContractState` already stores `generated_keys`; a parallel `existing_domains` view (the subset of `domains` whose keys are in `generated_keys`) should be exposed and used by `check_request_preconditions`. Only requests targeting the domain currently undergoing key generation need to be deferred. This mirrors the fix described in the external report: skip the unavailable component (the domain being initialized) rather than blocking all components.

---

### Proof of Concept

1. All N participants call `vote_add_domains` with a new domain config. After the N-th vote, the contract transitions to `Initializing`.
2. Key generation begins for the new domain. One Byzantine participant (participant index `k`, where `k < threshold`) deliberately goes offline and sends no DKG messages.
3. Key generation stalls. The contract remains in `Initializing`.
4. Any user calls `sign` (or `request_app_private_key` / `verify_foreign_transaction`) targeting any existing, fully-keyed domain.
5. `check_request_preconditions` calls `self.protocol_state.domain_registry()`, which hits the `_ => return Err(...)` arm and returns `InvalidState::ProtocolStateNotRunningNorResharing`.
6. `env::panic_str` is called; the transaction reverts. All users are blocked.
7. The freeze persists until honest participants organize a `vote_cancel_keygen` quorum, which itself requires threshold coordination and on-chain transactions — a window entirely controlled by the Byzantine participant's offline duration.

### Citations

**File:** crates/contract/src/state.rs (L34-42)
```rust
    pub fn domain_registry(&self) -> Result<&DomainRegistry, Error> {
        let domain_registry = match self {
            ProtocolContractState::Running(state) => &state.domains,
            ProtocolContractState::Resharing(state) => &state.previous_running_state.domains,
            _ => return Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
        };

        Ok(domain_registry)
    }
```

**File:** crates/contract/src/state.rs (L162-171)
```rust
    pub fn vote_cancel_keygen(
        &mut self,
        next_domain_id: u64,
    ) -> Result<Option<ProtocolContractState>, Error> {
        match self {
            ProtocolContractState::Initializing(state) => state.vote_cancel(next_domain_id),
            _ => Err(InvalidState::ProtocolStateNotInitializing.into()),
        }
        .map(|x| x.map(ProtocolContractState::Running))
    }
```

**File:** crates/contract/src/lib.rs (L241-305)
```rust
    /// Common preconditions enforced on every user-facing request method (`sign`,
    /// `request_app_private_key`, `verify_foreign_transaction`):
    ///
    /// 1. The target domain exists and its purpose matches `expected_purpose`.
    /// 2. The caller attached enough prepaid gas to perform the yield/resume flow.
    /// 3. The caller attached at least `minimum_deposit` (excess is refunded).
    /// 4. The contract is currently accepting user requests.
    ///
    /// Returns the validated domain config and the caller's account id.
    fn check_request_preconditions(
        &self,
        domain_id: DomainId,
        expected_purpose: DomainPurpose,
        minimum_gas: Gas,
        minimum_deposit: NearToken,
    ) -> (DomainConfig, AccountId) {
        // 1. Look up the domain and check its purpose.
        let domains = match self.protocol_state.domain_registry() {
            Ok(domains) => domains,
            Err(err) => env::panic_str(&err.to_string()),
        };
        let Some(domain_config) = domains.get_domain_by_domain_id(domain_id) else {
            env::panic_str(
                &InvalidParameters::DomainNotFound {
                    provided: domain_id,
                }
                .to_string(),
            );
        };
        if domain_config.purpose != expected_purpose {
            env::panic_str(
                &InvalidParameters::WrongDomainPurpose {
                    domain_id: domain_config.id,
                    expected: expected_purpose,
                    actual: domain_config.purpose,
                }
                .to_string(),
            );
        }
        let domain_config = domain_config.clone();

        // 2. Make sure the call will not run out of gas doing yield/resume logic.
        let prepaid_gas = env::prepaid_gas();
        if prepaid_gas < minimum_gas {
            env::panic_str(
                &InvalidParameters::InsufficientGas {
                    provided: prepaid_gas.as_gas(),
                    required: minimum_gas.as_gas(),
                }
                .to_string(),
            );
        }

        // 3. Require the minimum deposit and refund any excess.
        let predecessor = env::predecessor_account_id();
        require_deposit(minimum_deposit, &predecessor);

        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }

        (domain_config, predecessor)
    }
```

**File:** crates/contract/src/state/initializing.rs (L13-30)
```rust
/// In this state, we generate a new key for each new domain. At any given point of time, we are
/// generating the key of a single domain. After that, we move on to the next domain, or if there
/// are no more domains, transition into the Running state.
///
/// This state is reached by calling vote_add_domains from the Running state by a threshold number
/// of participants.
///
/// While generating the key for a domain, the `generating_key` field internally handles multiple
/// attempts as needed, only finishing when an attempt has succeeded.
///
/// Additionally, a threshold number of participants can vote to cancel this state; doing so will
/// revert back to the Running state but deleting the domains for which we have not yet successfully
/// generated a key. This can be useful if the current set of participants are no longer all online
/// and we wish to perform a resharing before adding domains again.
#[near(serializers=[borsh, json])]
#[derive(Debug)]
#[cfg_attr(feature = "dev-utils", derive(Clone, PartialEq))]
pub struct InitializingContractState {
```

**File:** crates/contract/src/state/running.rs (L237-249)
```rust
        if self.parameters.participants().len() as u64 == n_votes {
            let new_domains = self.domains.add_domains(domains.clone())?;
            Ok(Some(InitializingContractState {
                generated_keys: self.keyset.domains.clone(),
                domains: new_domains,
                epoch_id: self.keyset.epoch_id,
                generating_key: KeyEvent::new(
                    self.keyset.epoch_id,
                    domains[0].clone(),
                    self.parameters.clone(),
                ),
                cancel_votes: BTreeSet::new(),
            }))
```
