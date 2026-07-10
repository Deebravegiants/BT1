### Title
Unprotected `init()` Can Be Front-Run to Seize Full Control of MPC Participant Set — (`File: crates/contract/src/lib.rs`)

---

### Summary

The `init()` function in `crates/contract/src/lib.rs` lacks the `#[private]` attribute, allowing any external NEAR account to call it before the legitimate operator. Because `#[init]` functions can only succeed once (they fail if state already exists), a front-runner who calls `init()` first with attacker-controlled participants and `threshold=1` permanently seizes control of the MPC network's signing authority.

---

### Finding Description

The `init()` function is decorated with `#[init]` but **not** `#[private]`:

```rust
// crates/contract/src/lib.rs, line 1924-1926
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

In NEAR SDK, `#[private]` enforces `predecessor_account_id == current_account_id`, restricting a method to self-calls only. Without it, any NEAR account can invoke `init()`. The function sets the critical `parameters` — the participant set and governance threshold — that govern the entire MPC network. Once called, the contract transitions from `NotInitialized` to `Running` state, and any subsequent call to `init()` fails because state already exists.

The contract's own README confirms the two-step deployment pattern that creates the race window:

> "After deploying the contract, it will first be in an uninitialized state. The owner will need to initialize it via `init`..."

By contrast, `init_running()` at line 1979 correctly uses `#[private]`, and the sandbox test at `crates/contract/tests/sandbox/upgrade_to_current_contract.rs:438` explicitly verifies that external callers are rejected for `init_running`. No equivalent protection exists for `init()`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

---

### Impact Explanation

An attacker who front-runs `init()` can supply an arbitrary `ThresholdParameters` — for example, a single-participant set with `threshold=1` where the sole participant is the attacker's own NEAR account. This results in:

1. **Permanent seizure of the MPC participant set.** The legitimate operator's subsequent `init()` call fails because state already exists.
2. **Unauthorized threshold signature issuance.** With `threshold=1` and sole participant control, the attacker can respond to any `sign`, `request_app_private_key`, or `verify_foreign_transaction` request and produce valid threshold signatures without any honest-node participation.
3. **Unauthorized key derivation.** The attacker controls all CKD (Confidential Key Derivation) outputs.

This matches the allowed Critical impact: *"Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization"* and *"Bypass of threshold-signature requirements."* [5](#0-4) 

---

### Likelihood Explanation

- The vulnerability window is the time between contract deployment and the legitimate `init()` call. These are always **separate transactions** in NEAR when following the documented deployment procedure.
- An attacker monitoring the NEAR blockchain for a new deployment of the MPC contract WASM can detect it within one block and immediately submit their own `init()` call.
- The attack requires no special privileges — only a funded NEAR account.
- The attack is permanent: once `init()` succeeds, the state is set and cannot be overwritten by another `init()` call.

---

### Recommendation

1. **Combine deployment and initialization in a single transaction** using NEAR's `DeployContract` + `FunctionCall` batch action. This eliminates the race window entirely.
2. **Alternatively**, add an explicit caller check inside `init()`:
   ```rust
   require!(
       env::predecessor_account_id() == env::current_account_id(),
       "init can only be called by the contract account"
   );
   ```
   This mirrors the protection already applied to `init_running()` via `#[private]`. [2](#0-1) 

---

### Proof of Concept

1. Attacker monitors NEAR for deployment of the MPC contract WASM.
2. In the next block, attacker submits:
   ```json
   {
     "parameters": {
       "participants": [["attacker.near", 0, {"tls_public_key": "...", "url": "http://attacker.com"}]],
       "threshold": 1
     }
   }
   ```
   to `mpc-contract.near::init(...)`.
3. The contract transitions to `Running` state with `attacker.near` as the sole participant.
4. The legitimate operator's `init()` call fails: contract state already exists.
5. Attacker calls `vote_add_domains(...)` to register signing domains, then responds to any user `sign()` request via `respond(...)`, issuing valid threshold signatures for arbitrary foreign-chain transactions — all without any honest MPC node involvement. [6](#0-5) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L1924-1973)
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

        Ok(Self {
            protocol_state: ProtocolContractState::Running(RunningContractState::new(
                DomainRegistry::default(),
                Keyset::new(EpochId::new(0), Vec::new()),
                parameters,
                AddDomainsVotes::default(),
            )),
            pending_signature_requests: LookupMap::new(StorageKey::PendingSignatureRequestsV4),
            pending_ckd_requests: LookupMap::new(StorageKey::PendingCKDRequestsV3),
            pending_verify_foreign_tx_requests: LookupMap::new(
                StorageKey::PendingVerifyForeignTxRequestsV2,
            ),
            proposed_updates: ProposedUpdates::default(),
            config: init_config.map(Into::into).unwrap_or_default(),
            tee_state,
            accept_requests: true,
            node_migrations: NodeMigrations::default(),
            metrics: Default::default(),
            node_foreign_chain_support: Default::default(),
            foreign_chains: Lazy::new(
                StorageKey::ForeignChainMetadata,
                ForeignChainsMetadata::default(),
            ),
            tee_verifier_account_id: None,
            tee_verifier_votes: TeeVerifierVotes::default(),
        })
    }
```

**File:** crates/contract/src/lib.rs (L1975-1979)
```rust
    // This function can be used to transfer the MPC network to a new contract.
    #[private]
    #[init]
    #[handle_result]
    pub fn init_running(
```

**File:** crates/contract/tests/sandbox/upgrade_to_current_contract.rs (L438-474)
```rust
async fn init_running_rejects_external_callers_pre_initialization() {
    let (worker, contract) = init().await;
    let number_of_participants = 2;
    let (accounts, participants) = gen_accounts(&worker, number_of_participants).await;

    let threshold_parameters = ThresholdParameters::new(
        participants.clone(),
        Threshold::new(number_of_participants as u64),
    )
    .unwrap();

    let init_running_args = serde_json::json!({
            "domains": [],
            "next_domain_id": 0,
            "keyset": Keyset::new(EpochId::new(2), vec![]),
            "parameters": threshold_parameters,
    });

    let execution_error = accounts[0]
        .call(contract.id(), method_names::INIT_RUNNING)
        .max_gas()
        .args_json(init_running_args)
        .transact()
        .await
        .unwrap()
        .into_result()
        .expect_err("method is private and not callable from participant account.");

    let error_message = format!("{:?}", execution_error);

    let expected_error_message = "Smart contract panicked: Method init_running is private";

    assert!(
        error_message.contains(expected_error_message),
        "init_running call was accepted by external caller. expected method to be private. {:?}",
        error_message
    )
```

**File:** crates/contract/README.md (L233-237)
```markdown
### Deployment

After deploying the contract, it will first be in an uninitialized state. The owner will need to initialize it via `init`, providing the set of participants and threshold parameters.

The contract will then switch to running state, where further operations (like initializing keys, or changing the participant set), can be taken.
```
