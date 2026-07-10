### Title
Unguarded `init` Function Allows Any Caller to Frontrun Contract Initialization and Seize Full Control of the MPC Participant Set - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `MpcContract::init` function carries no access-control guard. Any NEAR account can call it in the window between contract deployment and the legitimate operator's initialization transaction. A successful frontrun installs the attacker's own accounts as the sole participants, giving them complete control over the MPC key-generation process and all subsequent threshold-signature issuance.

---

### Finding Description

`MpcContract::init` is decorated only with `#[init]` (the NEAR SDK attribute that prevents a second call once state exists) and `#[handle_result]`. It performs no caller check whatsoever:

```rust
// crates/contract/src/lib.rs  lines 1924-1973
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
    let parameters: ThresholdParameters = parameters.try_into_contract_type()?;
    ...
    parameters.validate()?;
    let initial_participants = parameters.participants();
    let tee_state = TeeState::with_mocked_participant_attestations(initial_participants);
    Ok(Self { ... })
}
``` [1](#0-0) 

Compare with the two other init-style functions in the same block, both of which carry `#[private]` (callable only by the contract account itself):

```rust
#[private]   // ← present
#[init]
pub fn init_running(...) { ... }

#[private]   // ← present
#[init(ignore_state)]
pub fn migrate() { ... }
``` [2](#0-1) [3](#0-2) 

`init` is the only initialization entry-point that is publicly callable by any account.

The minimum valid parameter set that passes `parameters.validate()` is two attacker-controlled accounts with threshold = 2 (satisfying the absolute minimum of 2 and the ≥ 60% relative lower bound):

```rust
// crates/contract/src/primitives/thresholds.rs  lines 56-83
const MIN_THRESHOLD_ABSOLUTE: u64 = 2;
fn governance_threshold_lower_relative_bound(n: u64) -> u64 {
    3_u64.saturating_mul(n).div_ceil(5)   // ceil(0.6 * n)
}
``` [4](#0-3) [5](#0-4) 

Additionally, `init` calls `TeeState::with_mocked_participant_attestations` for the supplied participants, meaning the attacker's accounts receive pre-approved mocked TEE attestations automatically — no genuine TEE quote is required for the initial participant set. [6](#0-5) 

---

### Impact Explanation

**Critical — Unauthorized threshold-signature issuance and full MPC key-share control.**

After a successful frontrun:

1. The attacker's accounts are the only recognized participants in `RunningContractState`.
2. The attacker calls `vote_add_domains` (participant-gated, but the attacker is the only participant) to add signing domains.
3. The attacker participates in DKG (`start_keygen_instance` / `vote_pk`) as the sole participant set, generating MPC key shares entirely under their control.
4. The attacker can call `respond` / `respond_ckd` to fulfill any user signature or CKD request with signatures derived from keys they control.
5. The legitimate operator's `init` call fails because `#[init]` prevents re-initialization once state exists, forcing a full contract redeploy — but any user who interacted with the compromised contract in the interim has already received attacker-controlled signatures.

This directly satisfies: *"Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization."*

---

### Likelihood Explanation

**Medium.**

- NEAR transactions are broadcast publicly before finalization; a monitoring attacker can observe the deployment transaction and submit a competing `init` call targeting the same block or the next one.
- The attacker needs only two funded NEAR accounts — no special hardware, no TEE, no key material.
- The attack window exists every time the contract is (re)deployed, including upgrades that reset state via `migrate`.
- The only practical mitigation today is deploying and calling `init` atomically in a single transaction batch, which is not enforced by the contract itself.

---

### Recommendation

Add `#[private]` to `init`, identical to `init_running` and `migrate`. In NEAR SDK, `#[private]` restricts the call to `predecessor_account_id == env::current_account_id()`, meaning only the contract account itself (i.e., the deployer acting through a batch transaction) can invoke it:

```rust
#[handle_result]
#[init]
#[private]          // ← add this
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> { ... }
```

Alternatively, assert inside the function body:

```rust
assert_eq!(
    env::predecessor_account_id(),
    env::current_account_id(),
    "init must be called by the contract account"
);
```

Either approach ensures that only the account that owns the contract can initialize it, eliminating the frontrun window.

---

### Proof of Concept

1. Attacker monitors the NEAR network for a `DeployContract` action targeting the MPC contract account (e.g., `v1.signer`).
2. In the same block or the next, attacker submits:
   ```json
   {
     "account_id": "v1.signer",
     "method_name": "init",
     "args": {
       "parameters": {
         "participants": {
           "next_id": 2,
           "participants": [
             ["attacker1.near", 0, { ... }],
             ["attacker2.near", 1, { ... }]
           ]
         },
         "threshold": 2
       },
       "init_config": null
     }
   }
   ```
3. `parameters.validate()` passes: n=2, threshold=2 ≥ ceil(0.6×2)=2, threshold ≤ 2. [5](#0-4) 
4. `TeeState::with_mocked_participant_attestations` grants both attacker accounts mocked-valid attestations. [6](#0-5) 
5. Contract state is now `Running` with attacker-controlled participants. The legitimate operator's `init` call panics with "state already exists". [7](#0-6) 
6. Attacker calls `vote_add_domains` from both accounts to add a Secp256k1 signing domain, then drives DKG to completion, obtaining full control of the MPC key shares and all future signature outputs.

### Citations

**File:** crates/contract/src/lib.rs (L1924-1945)
```rust
    #[handle_result]
    #[init]
    pub fn init(
        parameters: dtos::ThresholdParameters,
        init_config: Option<dtos::InitConfig>,
    ) -> Result<Self, Error> {
        let parameters: ThresholdParameters = parameters.try_into_contract_type()?;
        // Log participant count and hash - full parameters exceed NEAR's 16KB log limit at ~100 participants
        let params_hash = env::sha256_array(borsh::to_vec(&parameters).unwrap());
        log!(
            "init: signer={}, num_participants={}, parameters_hash={:?}, init_config={:?}",
            env::signer_account_id(),
            parameters.participants().len(),
            params_hash,
            init_config,
        );
        parameters.validate()?;

        // TODO(#1087): Every participant must have a valid attestation, otherwise we risk
        // participants being immediately kicked out once contract transitions into running.
        let initial_participants = parameters.participants();
        let tee_state = TeeState::with_mocked_participant_attestations(initial_participants);
```

**File:** crates/contract/src/lib.rs (L1976-1979)
```rust
    #[private]
    #[init]
    #[handle_result]
    pub fn init_running(
```

**File:** crates/contract/src/lib.rs (L2060-2063)
```rust
    #[private]
    #[init(ignore_state)]
    #[handle_result]
    pub fn migrate() -> Result<Self, Error> {
```

**File:** crates/contract/src/primitives/thresholds.rs (L11-17)
```rust
const MIN_THRESHOLD_ABSOLUTE: u64 = 2;

/// Lower bound on the GovernanceThreshold for `n` participants: 60% rounded up.
/// Single source of truth shared by validation and test fixtures.
pub(crate) fn governance_threshold_lower_relative_bound(n: u64) -> u64 {
    3_u64.saturating_mul(n).div_ceil(5)
}
```

**File:** crates/contract/src/primitives/thresholds.rs (L56-84)
```rust
    fn validate_threshold(n_shares: u64, k: Threshold) -> Result<(), Error> {
        if k.value() > n_shares {
            return Err(InvalidThreshold::MaxRequirementFailed {
                max: n_shares,
                found: k.value(),
            }
            .into());
        }
        if k.value() < MIN_THRESHOLD_ABSOLUTE {
            return Err(InvalidThreshold::MinAbsRequirementFailed.into());
        }
        let lower_relative_bound = governance_threshold_lower_relative_bound(n_shares);
        if k.value() < lower_relative_bound {
            return Err(InvalidThreshold::MinRelRequirementFailed {
                required: lower_relative_bound,
                found: k.value(),
            }
            .into());
        }
        let upper_relative_bound = governance_threshold_upper_relative_bound(n_shares);
        if k.value() > upper_relative_bound {
            return Err(InvalidThreshold::MaxRelRequirementFailed {
                max: upper_relative_bound,
                found: k.value(),
            }
            .into());
        }
        Ok(())
    }
```
