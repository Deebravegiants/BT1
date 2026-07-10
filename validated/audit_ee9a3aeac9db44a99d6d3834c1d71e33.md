### Title
Unguarded `init` Allows Front-Running to Seize Full MPC Participant Control - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `MpcContract::init` function carries no access-control guard. Any unprivileged NEAR account can call it before the legitimate deployer does. Because the production deployment scripts separate contract deployment from initialization into two distinct transactions, a window exists in which an attacker can front-run the `init` call, install their own participant set, and gain exclusive control over the MPC network's key generation and signing capability.

---

### Finding Description

`MpcContract::init` is decorated only with `#[init]` (the NEAR SDK macro that prevents a *second* call once state exists) and `#[handle_result]`. It carries no `#[private]` guard and performs no `predecessor_account_id == current_account_id` check:

```rust
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
    let parameters: ThresholdParameters = parameters.try_into_contract_type()?;
    // ...
    parameters.validate()?;
    // ...
    Ok(Self { ... })
}
``` [1](#0-0) 

By contrast, the companion `init_running` function is correctly protected:

```rust
#[private]
#[init]
#[handle_result]
pub fn init_running(...) -> Result<Self, Error> {
``` [2](#0-1) 

The production TEE-cluster deployment script explicitly separates the two steps with a sleep between them:

```bash
near contract deploy "$MPC_CONTRACT_ACCOUNT" use-file "$MPC_CONTRACT_PATH" \
  without-init-call ...
near_sleep "deploy contract"
# ... later ...
near contract call-function as-transaction "$MPC_CONTRACT_ACCOUNT" init \
  file-args "$INIT_ARGS_JSON" ...
``` [3](#0-2) 

This creates a multi-block window between deployment and initialization. During that window, any NEAR account can call `init` with an arbitrary `ThresholdParameters`, because the only validation performed is structural (threshold ≥ 60 %, participant count ≥ 2, etc.):

```rust
parameters.validate()?;
``` [4](#0-3) 

Once `init` succeeds for the attacker, the NEAR SDK `#[init]` macro causes every subsequent `init` call — including the legitimate deployer's — to panic with "The contract has already been initialized."

The attacker-controlled `RunningContractState` is then the sole governance authority. All subsequent governance actions (`vote_new_parameters`, `vote_add_domains`, `respond`, etc.) are gated on membership in the participant set stored at initialization:

```rust
fn assert_caller_is_attested_participant_and_protocol_active(&self) { ... }
``` [5](#0-4) 

The attacker's accounts pass every participant check; the legitimate operators' accounts do not.

---

### Impact Explanation

**Critical.** An attacker who wins the front-run owns the entire MPC network:

- They are the only participants recognized by the contract.
- They call `vote_add_domains` unanimously (all participants are theirs) to generate signing keys.
- They hold all key shares and can produce threshold signatures for any payload — including foreign-chain transactions — without any authorization from the intended operators.
- All funds routed through the chain-signature contract or verified foreign-chain flow are under attacker control.

This satisfies: *"Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization"* and *"Bypass of threshold-signature requirements or unauthorized access to MPC key shares, signing capability, or secret material."*

---

### Likelihood Explanation

**Medium.** The attack requires:

1. Watching the NEAR blockchain for the contract deployment transaction (trivially automated).
2. Submitting an `init` call in the next block before the deployer does (standard front-running; NEAR blocks are ~1 s).
3. The deployment scripts deliberately insert a sleep between deployment and initialization, making the window reliably several seconds wide.

No privileged access, no TEE bypass, no collusion, and no leaked key is required. Any NEAR account with enough gas can execute this.

---

### Recommendation

1. **Add `#[private]`** to `init`, matching the protection already present on `init_running`. This restricts the call to the contract account itself (i.e., only a transaction signed by the contract account's full-access key succeeds):

   ```rust
   #[private]
   #[handle_result]
   #[init]
   pub fn init(
       parameters: dtos::ThresholdParameters,
       init_config: Option<dtos::InitConfig>,
   ) -> Result<Self, Error> { ... }
   ```

2. **Alternatively**, deploy and initialize in a single transaction using NEAR CLI's `--init-call` flag, eliminating the window entirely.

3. **Deployment scripts** should be updated to use `--init-call` or to assert that `init` is called atomically with deployment.

---

### Proof of Concept

```
# Step 1 – Deployer deploys the contract (without init call)
near contract deploy v1.signer use-file mpc_contract.wasm \
  without-init-call network-config mainnet sign-with-keychain send

# Step 2 – Attacker (any NEAR account) races to call init first
near contract call-function as-transaction v1.signer init \
  json-args '{
    "parameters": {
      "threshold": 2,
      "participants": {
        "next_id": 2,
        "participants": [
          ["attacker-node-0.near", 0, {"tls_public_key":"ed25519:ATTACKER_KEY_0","url":"https://attacker0.example"}],
          ["attacker-node-1.near", 1, {"tls_public_key":"ed25519:ATTACKER_KEY_1","url":"https://attacker1.example"}]
        ]
      }
    }
  }' \
  prepaid-gas '300.0 Tgas' attached-deposit '0 NEAR' \
  sign-as attacker.near network-config mainnet sign-with-keychain send

# Step 3 – Deployer's init call fails:
# "The contract has already been initialized"

# Step 4 – Attacker's two nodes call vote_add_domains unanimously,
#           generate keys, and can now sign any payload.
```

The attacker's `init` call satisfies `parameters.validate()` (2 participants, threshold 2 = 100 % ≥ 60 %) and is accepted. The legitimate deployer's call is permanently rejected. The attacker's nodes hold all key shares and can issue threshold signatures for any request submitted to the contract.

### Citations

**File:** crates/contract/src/lib.rs (L569-573)
```rust
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();
```

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

**File:** crates/contract/src/lib.rs (L1976-1986)
```rust
    #[private]
    #[init]
    #[handle_result]
    pub fn init_running(
        domains: Vec<DomainConfig>,
        next_domain_id: u64,
        keyset: Keyset,
        parameters: dtos::ThresholdParameters,
        init_config: Option<dtos::InitConfig>,
    ) -> Result<Self, Error> {
        let parameters: ThresholdParameters = parameters.try_into_contract_type()?;
```

**File:** localnet/tee/scripts/rust-launcher/deploy-tee-cluster.sh (L1141-1183)
```shellscript
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
