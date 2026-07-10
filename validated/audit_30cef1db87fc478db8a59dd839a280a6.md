### Title
Unguarded `init` Enables Front-Running of MPC Contract Initialization — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `MpcContract::init` function carries no `#[private]` guard. The official deployment procedure deploys the contract WASM in one transaction (`without-init-call`) and calls `init` in a separate, later transaction. Any external account can observe the deploy transaction and race to call `init` first, supplying attacker-controlled `parameters` (participant set, threshold). This gives the attacker full control of the MPC network before the legitimate operators can initialize it.

---

### Finding Description

`MpcContract::init` is declared as:

```rust
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
``` [1](#0-0) 

There is no `#[private]` attribute. Compare with `init_running` and `migrate`, which are both correctly guarded:

```rust
#[private]
#[init]
pub fn init_running(...) { ... }

#[private]
#[init(ignore_state)]
pub fn migrate() { ... }
``` [2](#0-1) [3](#0-2) 

The official deployment procedure is explicitly two-step and documented across multiple guides:

```bash
# Step 1 – deploy WASM, no init call
near contract deploy $MPC_CONTRACT_ACCOUNT use-file "$MPC_CONTRACT_PATH" \
  without-init-call network-config testnet sign-with-keychain send

# Step 2 – initialize (separate transaction, later)
near contract call-function as-transaction $MPC_CONTRACT_ACCOUNT init \
  file-args /tmp/$USER/init_args.json ...
``` [4](#0-3) [5](#0-4) [6](#0-5) 

Between the deploy transaction and the `init` transaction, the contract state is `NotInitialized` and `init` is callable by anyone. [7](#0-6) 

---

### Impact Explanation

An attacker who front-runs `init` supplies their own `ThresholdParameters`, setting themselves as the sole participant with `threshold = 1`. The contract transitions directly into `ProtocolContractState::Running` with the attacker's participant set and keyset epoch 0. [8](#0-7) 

From that point the attacker:
- Is the only recognized participant; all legitimate governance calls (`vote_new_parameters`, `vote_add_domains`, etc.) require participant authentication and will reject the real operators.
- Can unilaterally drive key generation (`start_keygen_instance`, `vote_pk`) to produce a threshold key under their sole control.
- Can issue threshold signatures and CKD outputs for any foreign-chain transaction without any co-signer.

This satisfies **Critical – Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization**.

---

### Likelihood Explanation

**High.** Every fresh deployment follows the documented two-step flow. The gap between the deploy transaction and the `init` transaction is observable on-chain by any NEAR account. No special privilege, key material, or collusion is required — only the ability to submit a NEAR transaction faster than the deployer. The `init` function accepts arbitrary `ThresholdParameters` with no caller restriction.

---

### Recommendation

Add `#[private]` to `init`, mirroring `init_running` and `migrate`:

```rust
#[private]
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

In NEAR, `#[private]` restricts the call to `predecessor_account_id == current_account_id`, meaning only the contract account itself can call `init`. The deployer would then use `near contract deploy ... with-init-call` (atomic deploy + init in one transaction) or call `init` as the contract account in the same transaction batch, eliminating the front-running window entirely. [1](#0-0) 

---

### Proof of Concept

1. Operator broadcasts: `near contract deploy mpc-contract.near use-file mpc.wasm without-init-call ...`
2. Attacker observes the deploy transaction on-chain (contract is now deployed, state = `NotInitialized`).
3. Attacker broadcasts before the operator's `init` transaction:
   ```bash
   near contract call-function as-transaction mpc-contract.near init \
     json-args '{"parameters": {"threshold": 1, "participants": {"next_id": 1, "participants": [["attacker.near", 0, {"url": "...", "tls_public_key": "..."}]]}}}' \
     sign-as attacker.near ...
   ```
4. Contract enters `Running` state with `attacker.near` as the sole participant at threshold 1.
5. All subsequent calls from the legitimate operators fail with `NotParticipant`.
6. Attacker drives key generation alone and gains sole signing authority over all foreign-chain transactions routed through the MPC network. [9](#0-8)

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

**File:** docs/testnet/setup-guide-for-testnet-with-tee-support.md (L115-119)
```markdown
Deploy the MPC contract:

```bash
near contract deploy $MPC_CONTRACT_ACCOUNT use-file "$MPC_CONTRACT_PATH" without-init-call network-config testnet sign-with-keychain send
```
```

**File:** localnet/tee/scripts/rust-launcher/deploy-tee-cluster.sh (L1139-1183)
```shellscript
deploy_contract() {
  log "Deploying MPC contract to $MPC_CONTRACT_ACCOUNT"
  # FIX #5: retry wrapper + sleep
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

  near_sleep "init contract"
}
```

**File:** docs/localnet/localnet.md (L128-132)
```markdown
Now we can deploy the contract with this command.

```shell
near contract deploy mpc-contract.test.near use-file "$MPC_CONTRACT_PATH" without-init-call network-config mpc-localnet sign-with-keychain send
```
```

**File:** crates/contract/src/state.rs (L206-213)
```rust
    pub fn name(&self) -> &'static str {
        match self {
            ProtocolContractState::NotInitialized => "NotInitialized",
            ProtocolContractState::Initializing(_) => "Initializing",
            ProtocolContractState::Running(_) => "Running",
            ProtocolContractState::Resharing(_) => "Resharing",
        }
    }
```
