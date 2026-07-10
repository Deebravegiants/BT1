### Title
Unprotected `init` Function Allows Front-Running to Seize Full Control of MPC Participant Set - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `init` function of the MPC contract lacks a `#[private]` access guard. Because the deployment process deploys the contract and calls `init` in two separate transactions, any unprivileged NEAR account can race to call `init` first with attacker-controlled parameters, installing themselves as the sole participant with a threshold of 1 and taking full control of the MPC network before legitimate operators can initialize it.

---

### Finding Description

The `init` function is the sole entry point that transitions the contract from `NotInitialized` to `Running` and sets the authoritative participant set and threshold for the entire MPC network. [1](#0-0) 

It carries only `#[init]` (which prevents re-initialization once state exists) but **not** `#[private]` (which would restrict the caller to the contract account itself). Compare this to `init_running` and `migrate`, which both carry `#[private]`: [2](#0-1) [3](#0-2) 

The deployment procedure in every documented flow deploys the contract binary and calls `init` as **two separate transactions**:

```bash
# Step 1 – deploy (no init call)
near contract deploy "$MPC_CONTRACT_ACCOUNT" use-file "$MPC_CONTRACT_PATH" \
  without-init-call ...

# Step 2 – init (separate transaction, separate block)
near contract call-function as-transaction "$MPC_CONTRACT_ACCOUNT" init \
  file-args "$INIT_ARGS_JSON" ...
``` [4](#0-3) 

The same two-step pattern appears in the localnet and testnet guides: [5](#0-4) 

Between the deploy transaction and the `init` transaction there is a window — potentially multiple blocks — during which the contract is live on-chain but uninitialized. Any account can call `init` during this window.

---

### Impact Explanation

An attacker who wins the race calls `init` with a `ThresholdParameters` struct that lists only their own account as a participant and sets `threshold = 1`. The contract transitions to `Running` with the attacker as the sole authorized participant. [6](#0-5) 

From that point the attacker can:

1. Call `vote_add_domains` (requires only threshold = 1 vote, i.e., their own) to trigger distributed key generation.
2. Participate in DKG as the only node, obtaining full control of the generated key shares.
3. Issue threshold signatures (`respond`) for arbitrary payloads on any supported foreign chain.
4. Perform confidential key derivation (`respond_ckd`) for any derivation path.

The legitimate deployer's subsequent `init` call will fail because state already exists, forcing a full re-deployment. If the attacker acts quickly enough to complete DKG before the compromise is detected, the generated key material is permanently under their control.

**Impact class:** Critical — Unauthorized threshold signature issuance and unauthorized access to MPC key shares without required participant authorization.

---

### Likelihood Explanation

- NEAR transactions are publicly visible in the mempool and on-chain. Any observer can detect a contract deployment and immediately submit a competing `init` call.
- No special privilege, leaked key, or collusion is required — only a funded NEAR account.
- The window between deploy and init is non-zero in every documented deployment procedure.
- The attack is fully deterministic and requires no brute-force or probabilistic success.

**Likelihood: High.**

---

### Recommendation

Add `#[private]` to `init`, consistent with `init_running` and `migrate`:

```rust
#[handle_result]
#[private]          // <-- add this
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

`#[private]` in NEAR restricts the caller to `env::current_account_id()`, meaning only the contract account itself can invoke the function. The deployer then uses the `--initFunction init` flag on the `near contract deploy` command so that deployment and initialization are **atomic in a single transaction**, eliminating the front-running window entirely. [7](#0-6) 

---

### Proof of Concept

1. Attacker monitors NEAR for a transaction deploying the MPC contract binary to account `v1.signer`.
2. In the same block or the next block, attacker submits:
   ```bash
   near contract call-function as-transaction v1.signer init \
     json-args '{
       "parameters": {
         "participants": {
           "next_id": 1,
           "participants": [["attacker.near", 0, {
             "tls_public_key": "<attacker_tls_key>",
             "url": "http://attacker.example.com"
           }]]
         },
         "threshold": 1
       }
     }' \
     prepaid-gas '300.0 Tgas' attached-deposit '0 NEAR' \
     sign-as attacker.near network-config mainnet sign-with-keychain send
   ```
3. If included before the legitimate `init`, the contract is now in `Running` state with `attacker.near` as the sole participant and threshold 1.
4. The legitimate deployer's `init` call panics with a state-already-exists error.
5. Attacker calls `vote_add_domains` to start key generation, then runs their own MPC node to complete DKG, gaining sole control of the threshold key shares.
6. Attacker can now call `respond` to issue valid threshold signatures for any payload on any foreign chain supported by the MPC network. [8](#0-7) [4](#0-3)

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

**File:** crates/contract/src/lib.rs (L2060-2063)
```rust
    #[private]
    #[init(ignore_state)]
    #[handle_result]
    pub fn migrate() -> Result<Self, Error> {
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

**File:** docs/localnet/localnet.md (L265-269)
```markdown
Now, we should be ready to call the `init` function on the contract.

```shell
near contract call-function as-transaction mpc-contract.test.near init file-args /tmp/init_args.json prepaid-gas '300.0 Tgas' attached-deposit '0 NEAR' sign-as mpc-contract.test.near network-config mpc-localnet sign-with-keychain send
```
```
