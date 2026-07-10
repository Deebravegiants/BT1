### Title
Unguarded `init` Allows Any Caller to Hijack MPC Contract Initialization - (File: crates/contract/src/lib.rs)

### Summary
The `MpcContract::init` function carries the `#[init]` attribute but **no** `#[private]` guard and no explicit caller check. Any NEAR account can call it on a freshly deployed but not-yet-initialized contract. An attacker who races the legitimate deployer can set themselves as the sole participant with threshold 1, gaining full unilateral control over the MPC signing network.

### Finding Description
In `crates/contract/src/lib.rs`, the three initialization entry-points are:

| Function | `#[init]` | `#[private]` |
|---|---|---|
| `init` | ✅ | ❌ |
| `init_running` | ✅ | ✅ |
| `migrate` | ✅ (`ignore_state`) | ✅ |

`init_running` and `migrate` are correctly restricted to the contract itself via `#[private]`. `init` is not. [1](#0-0) 

The `#[init]` macro in the NEAR SDK only prevents *re-initialization* (it panics if contract state already exists). It does **not** restrict which account may call the function. There is no `#[private]` attribute, no `env::predecessor_account_id() == env::current_account_id()` check, and no `assert_caller_is_signer` / `voter_or_panic` guard inside the function body. [2](#0-1) 

The deployment workflow (both testnet and localnet) deploys the WASM binary in one transaction and calls `init` in a separate, subsequent transaction: [3](#0-2) 

This creates a window — however brief — between deployment and initialization during which any account can call `init` with attacker-controlled `parameters`.

### Impact Explanation
An attacker who calls `init` first can supply:
- `parameters.participants` = a single account they control
- `parameters.threshold` = 1

The contract transitions immediately to `ProtocolContractState::Running` with the attacker as the sole participant. From that position the attacker can:
1. Call `vote_add_domains` to register signing domains.
2. Act as leader and follower in DKG (`start_keygen_instance` / `vote_pk`) to generate key shares they fully control.
3. Call `sign` / `respond` to issue threshold signatures for arbitrary foreign-chain transactions without any legitimate participant authorization.

This satisfies the **Critical** impact class: *Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization.*

### Likelihood Explanation
- The deployment scripts separate `deploy` and `init` into distinct transactions, creating a concrete race window.
- NEAR processes transactions per-shard in block order; an attacker monitoring the chain for a newly deployed but uninitialized contract account can submit their `init` call in the same or next block.
- No special privilege, key material, or collusion is required — any NEAR account with enough gas can exploit this.
- The attack is a one-shot, irreversible takeover: once `init` succeeds, the `#[init]` guard prevents any subsequent legitimate `init` call.

### Recommendation
Add `#[private]` to `init`, making it callable only by the contract account itself (i.e., the deployer must batch the deploy and init actions in a single transaction):

```rust
#[handle_result]
#[private]          // ← add this
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

Alternatively, add an explicit predecessor check inside the function body:

```rust
assert_eq!(
    env::predecessor_account_id(),
    env::current_account_id(),
    "init may only be called by the contract account"
);
```

This mirrors the protection already applied to `init_running` and `migrate`. [4](#0-3) 

### Proof of Concept
1. Legitimate deployer submits TX₁: `DeployContract(mpc_contract.wasm)` to account `mpc.near`.
2. Attacker observes TX₁ finalized; `mpc.near` has no state yet.
3. Attacker submits TX₂: `FunctionCall(mpc.near, "init", { parameters: { participants: [attacker.near, ...], threshold: 1 } })`.
4. TX₂ executes before the deployer's own `init` call; `MpcContract::init` succeeds, writing attacker-controlled state.
5. Deployer's subsequent `init` call panics: `"The contract has already been initialized"`.
6. Attacker, now the sole participant with threshold 1, calls `vote_add_domains`, drives DKG, and issues signatures for arbitrary foreign-chain transactions. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L1924-1929)
```rust
    #[handle_result]
    #[init]
    pub fn init(
        parameters: dtos::ThresholdParameters,
        init_config: Option<dtos::InitConfig>,
    ) -> Result<Self, Error> {
```

**File:** crates/contract/src/lib.rs (L1940-1945)
```rust
        parameters.validate()?;

        // TODO(#1087): Every participant must have a valid attestation, otherwise we risk
        // participants being immediately kicked out once contract transitions into running.
        let initial_participants = parameters.participants();
        let tee_state = TeeState::with_mocked_participant_attestations(initial_participants);
```

**File:** crates/contract/src/lib.rs (L1947-1953)
```rust
        Ok(Self {
            protocol_state: ProtocolContractState::Running(RunningContractState::new(
                DomainRegistry::default(),
                Keyset::new(EpochId::new(0), Vec::new()),
                parameters,
                AddDomainsVotes::default(),
            )),
```

**File:** crates/contract/src/lib.rs (L1975-1985)
```rust
    // This function can be used to transfer the MPC network to a new contract.
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
```

**File:** localnet/tee/scripts/rust-launcher/deploy-tee-cluster.sh (L1171-1183)
```shellscript
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
