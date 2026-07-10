### Title
Unprotected `init` Function Callable by Any Account Before Deployer — (`File: crates/contract/src/lib.rs`)

### Summary

The `MpcContract::init` function is decorated with `#[init]` but **not** `#[private]`, meaning any NEAR account can call it before the legitimate deployer does. A front-running attacker who calls `init` first installs an attacker-controlled participant set and threshold as the authoritative contract state. Because NEAR's `#[init]` macro panics if state already exists, the deployer's subsequent `init` call will fail, and the contract must be redeployed. If the attacker's initialization goes undetected, they control the governance participant set of the MPC network.

### Finding Description

`MpcContract::init` at line 1926 carries only `#[init]` — no `#[private]` attribute and no deployer/owner check inside the function body:

```rust
// crates/contract/src/lib.rs:1924-1929
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
``` [1](#0-0) 

By contrast, the sibling initializer `init_running` correctly adds `#[private]`:

```rust
// crates/contract/src/lib.rs:1976-1979
#[private]
#[init]
#[handle_result]
pub fn init_running(...)
``` [2](#0-1) 

And `migrate` also carries `#[private]`: [3](#0-2) 

The deployment scripts deploy the contract **without** an inline init call, creating a window between deployment and initialization:

```bash
# deploy-tee-cluster.sh line 1143-1144
near contract deploy "$MPC_CONTRACT_ACCOUNT" use-file "$MPC_CONTRACT_PATH" \
  without-init-call ...
# ... then separately:
near contract call-function as-transaction "$MPC_CONTRACT_ACCOUNT" init ...
``` [4](#0-3) 

During this window, any account can submit a transaction calling `init` with attacker-chosen `parameters` (participants, threshold, config). NEAR's `#[init]` macro enforces single-initialization: once state exists, any subsequent `init` call panics. The deployer's legitimate `init` call will therefore fail.

### Impact Explanation

An attacker who wins the race installs an arbitrary `ThresholdParameters` as the contract's authoritative state. Concretely:

1. **Participant-set takeover**: The attacker can list themselves as the sole participant with `threshold = 1`. All subsequent governance votes (`vote_add_domains`, `vote_new_parameters`, etc.) are gated on participant membership. With the attacker as the only participant, they unilaterally control the MPC network's governance state.
2. **Forced redeployment**: The deployer's `init` call fails; the contract account must be redeployed, disrupting the launch.
3. **Stealthy manipulation**: The attacker could include the legitimate participants but lower the threshold (e.g., from `t-of-n` to `1-of-n`), making the manipulation harder to detect at a glance while granting themselves unilateral governance power.

`vote_add_domains` and `vote_new_parameters` only call `assert_caller_is_signer()` (signer == predecessor), not a TEE-attestation check, so an attacker listed as a participant can cast governance votes without a TEE node: [5](#0-4) 

This maps to the allowed impact: **participant-state manipulation that breaks production safety/accounting invariants** (Medium), with escalation potential toward unauthorized governance control of the MPC signing network.

### Likelihood Explanation

- The deployment scripts explicitly separate `deploy` from `init` (two distinct transactions), creating a real, observable window.
- Any NEAR account can submit a transaction; no special privilege is required.
- NEAR block times are ~1 second; a monitoring bot watching the mempool or block explorer for a new contract deployment can front-run the init call reliably.
- The attack requires no threshold collusion, no TEE access, and no leaked keys.

### Recommendation

Add `#[private]` to `init`, which in NEAR SDK restricts the call to `predecessor_account_id == current_account_id` (i.e., only the contract account itself can call it):

```rust
#[handle_result]
#[init]
#[private]          // ← add this
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

Alternatively, combine deployment and initialization in a single transaction using NEAR CLI's `with-init-call` flag, eliminating the window entirely.

### Proof of Concept

1. Deployer broadcasts: `near contract deploy mpc-contract.near use-file mpc.wasm without-init-call ...`
2. Attacker observes the deployment transaction in the mempool or in the next block.
3. Attacker immediately broadcasts: `near contract call-function as-transaction mpc-contract.near init args '{"parameters": {"threshold": 1, "participants": {"next_id": 1, "participants": [["attacker.near", 0, {...}]]}}}' sign-as attacker.near ...`
4. Attacker's `init` succeeds; contract state is now `Running` with `attacker.near` as the sole participant at threshold 1.
5. Deployer's `init` call fails: `"Smart contract panicked: The contract has already been initialized"`.
6. Attacker calls `vote_add_domains` (no TEE check required, only `assert_caller_is_signer`) to drive the contract into `Initializing` state.
7. Deployer must redeploy; if the manipulation is subtle (attacker included alongside legitimate participants with a lowered threshold), it may go undetected. [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L2423-2434)
```rust
    fn assert_caller_is_signer() -> AccountId {
        let signer_id = env::signer_account_id();
        let predecessor_id = env::predecessor_account_id();

        assert_eq!(
            signer_id, predecessor_id,
            "Caller must be the signer account (signer: {}, predecessor: {})",
            signer_id, predecessor_id
        );

        signer_id
    }
```

**File:** localnet/tee/scripts/rust-launcher/deploy-tee-cluster.sh (L1142-1180)
```shellscript
  near_tx_retry "deploy contract to $MPC_CONTRACT_ACCOUNT" \
     near contract deploy "$MPC_CONTRACT_ACCOUNT" use-file "$MPC_CONTRACT_PATH" \
      without-init-call network-config "$NEAR_NETWORK_CONFIG" sign-with-keychain send
  near_sleep "deploy contract"
}

add_node_keys_from_file() {
  local keys_file="$1"
  log "Adding node keys to NEAR accounts using $keys_file"
  [ -f "$keys_file" ] || { err "Missing keys file at $keys_file. Run collect phase first."; exit 1; }

  jq -c '.[]' "$keys_file" | while read -r row; do
    local acct signer responder
    acct="$(echo "$row" | jq -r .account)"
    signer="$(echo "$row" | jq -r .signer_pk)"
    responder="$(echo "$row" | jq -r .responder_pk)"

    log "$acct: add signer key"
    near_add_key_skip_if_exists "$acct" "$signer" "signer"

    log "$acct: add responder key"
    near_add_key_skip_if_exists "$acct" "$responder" "responder"
  done
}

add_node_keys_from_keysjson() {
  add_node_keys_from_file "$KEYS_JSON"
}

init_contract() {
  log "Initializing contract using $INIT_ARGS_JSON"
  [ -f "$INIT_ARGS_JSON" ] || { err "Missing init_args.json at $INIT_ARGS_JSON. Run init_args phase first."; exit 1; }

  # FIX #5: retry wrapper + sleep
  near_tx_retry "init contract $MPC_CONTRACT_ACCOUNT" \
     near contract call-function as-transaction "$MPC_CONTRACT_ACCOUNT" init \
      file-args "$INIT_ARGS_JSON" prepaid-gas '300.0 Tgas' \
      attached-deposit '0 NEAR' sign-as "$MPC_CONTRACT_ACCOUNT" \
      network-config "$NEAR_NETWORK_CONFIG" sign-with-keychain send
```
