### Title
Unguarded `init` Function Allows Any Caller to Front-Run Contract Initialization and Seize Full MPC Network Control - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `init` function in the MPC NEAR contract lacks the `#[private]` access guard present on `init_running`. Because the production deployment workflow deploys the contract and calls `init` in separate transactions, any unprivileged NEAR account can front-run the initialization window, inject themselves as the sole participant with threshold=1, and permanently seize governance and signing authority over the entire MPC network.

---

### Finding Description

The `init` function at `crates/contract/src/lib.rs:1924–1973` is decorated only with `#[init]` (NEAR's one-time initialization guard) but **not** with `#[private]` (which restricts the caller to `predecessor_account_id == current_account_id`, i.e., the contract account itself):

```rust
// crates/contract/src/lib.rs:1924-1929
#[handle_result]
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
``` [1](#0-0) 

Compare with `init_running`, which correctly carries `#[private]`:

```rust
// crates/contract/src/lib.rs:1976-1979
#[private]
#[init]
#[handle_result]
pub fn init_running(
``` [2](#0-1) 

The production deployment scripts explicitly deploy the contract **without** an init call, then call `init` in a separate transaction with a sleep in between:

```bash
# deploy-tee-cluster.sh:1142-1144
near contract deploy "$MPC_CONTRACT_ACCOUNT" use-file "$MPC_CONTRACT_PATH" \
  without-init-call network-config "$NEAR_NETWORK_CONFIG" sign-with-keychain send
near_sleep "deploy contract"
# ... later ...
near contract call-function as-transaction "$MPC_CONTRACT_ACCOUNT" init \
  file-args "$INIT_ARGS_JSON" ...
``` [3](#0-2) 

This creates a multi-block window during which the contract is deployed but uninitialized. Because `init` has no caller restriction, any NEAR account can call it first with attacker-controlled `parameters`.

Inside `init`, the only check is `parameters.validate()`, which accepts a single participant with threshold=1 as valid. The call then invokes `TeeState::with_mocked_participant_attestations`, which stores a `VerifiedAttestation::Mock(MockAttestation::Valid)` entry for every supplied participant — bypassing real TEE verification entirely:

```rust
// crates/contract/src/tee/tee_state.rs:131-139
tee_state.stored_attestations.insert(
    tls_public_key,
    NodeAttestation {
        node_id,
        verified_attestation: VerifiedAttestation::Mock(
            attestation::MockAttestation::Valid,
        ),
    },
);
``` [4](#0-3) 

Once the attacker's `init` call lands, the contract is permanently initialized (NEAR's `#[init]` prevents re-initialization). The legitimate operator's subsequent `init` call will panic and fail.

---

### Impact Explanation

**Critical.** An attacker who wins the initialization race:

1. Becomes the sole registered participant with threshold=1, giving them unilateral governance authority.
2. Calls `vote_add_domains` as the only participant — a single vote immediately reaches the threshold and transitions the contract to `Initializing` state.
3. Runs their own MPC node as the sole participant; with threshold=1, that node alone generates all key shares and can produce valid threshold signatures.
4. All subsequent `sign`, `request_app_private_key`, and `verify_foreign_transaction` requests are processed exclusively by the attacker's node.

The legitimate operator cannot recover: `#[init]` prevents re-initialization, and the attacker controls all governance votes needed to reshare or replace participants. [5](#0-4) 

---

### Likelihood Explanation

**High.** The production deployment workflow (`deploy-tee-cluster.sh`, `launch-localnet.sh`, testnet setup guide) consistently separates contract deployment from initialization across multiple blocks, with explicit `sleep` calls between them. Any account monitoring the NEAR blockchain for newly deployed but uninitialized contracts can detect the window and submit a competing `init` call. No privileged access, leaked keys, or collusion is required — only the ability to submit a NEAR transaction. [3](#0-2) 

---

### Recommendation

Add `#[private]` to the `init` function, mirroring the protection already applied to `init_running`:

```rust
#[handle_result]
#[private]   // ← add this
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

Alternatively, deploy and initialize in a single atomic transaction using NEAR's `--init-function` / `with-init-call` flag so no uninitialized window exists on-chain. [1](#0-0) 

---

### Proof of Concept

1. Operator deploys the contract without initialization:
   ```bash
   near contract deploy mpc-contract.near use-file mpc.wasm without-init-call ...
   ```
2. Attacker observes the deployment on-chain and immediately submits:
   ```bash
   near contract call-function as-transaction mpc-contract.near init \
     json-args '{
       "parameters": {
         "threshold": 1,
         "participants": {
           "next_id": 1,
           "participants": [["attacker.near", 0, {
             "tls_public_key": "<attacker_tls_key>",
             "url": "https://attacker-node.example.com"
           }]]
         }
       }
     }' sign-as attacker.near ...
   ```
3. `init` succeeds: the contract is now in `Running` state with `attacker.near` as the sole participant, threshold=1, and a `Mock(Valid)` attestation stored for the attacker's TLS key.
4. Operator's subsequent `init` call panics: `"The contract has already been initialized"`.
5. Attacker calls `vote_add_domains` from `attacker.near` — one vote equals threshold, domains are added.
6. Attacker's MPC node (threshold=1) generates all key shares and begins serving signing requests, issuing unauthorized threshold signatures for any payload. [6](#0-5) [7](#0-6)

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

**File:** crates/contract/src/tee/tee_state.rs (L104-143)
```rust
    pub(crate) fn with_mocked_participant_attestations(participants: &Participants) -> Self {
        let mut tee_state = Self::default();

        for (account_id, _, participant_info) in participants.participants() {
            let tls_public_key = participant_info.tls_public_key.clone();
            // TODO(#1087): replace account_public_key with a real account public
            // key passed in by the caller. `Participants` does not currently
            // carry the operator's account public key, so a mocked entry
            // cannot record the real one and we use the TLS key as a unique
            // per-participant placeholder. The mock keeps the
            // participant from being kicked out of an empty `TeeState` until
            // a real `submit_participant_info` call replaces it (keyed by
            // TLS), but any caller-facing check that compares
            // `signer_account_pk` against the stored key will fail until
            // then. #1087 tracks threading real attestations through
            // initialization so this sentinel can go away.
            let node_id = NodeId {
                account_id: account_id.clone(),
                tls_public_key: tls_public_key.clone(),
                // Use tls_public_key as account_public_key instead of hardcoded
                // Ed25519PublicKey::from([0u8; 32]) so that same account public
                // key isn't associated with different tls keys.
                // This is not a fix for above issue: #1087, which should be
                // addressed outside this PR.
                account_public_key: tls_public_key.clone(),
            };

            tee_state.stored_attestations.insert(
                tls_public_key,
                NodeAttestation {
                    node_id,
                    verified_attestation: VerifiedAttestation::Mock(
                        attestation::MockAttestation::Valid,
                    ),
                },
            );
        }

        tee_state
    }
```
