### Title
Unprotected `init` Function Allows Frontrunning to Install Attacker-Controlled Participant Set - (File: `crates/contract/src/lib.rs`)

### Summary

The `init` function in the MPC contract lacks the `#[private]` access-control attribute present on every other privileged initializer (`init_running`, `migrate`). Any unprivileged NEAR account can call `init` before the legitimate operator does, installing an attacker-controlled participant set and threshold, and thereby seizing full control of the MPC signing network.

### Finding Description

The MPC contract is deployed in an uninitialized state and then initialized via a separate `init` transaction. The `init` function is decorated with `#[handle_result]` and `#[init]` but **not** `#[private]`: [1](#0-0) 

In NEAR SDK, `#[init]` only prevents re-initialization once state exists; it does **not** restrict the caller. The `#[private]` attribute is the mechanism that enforces `predecessor_account_id == current_account_id`. Both sibling initializers use it: [2](#0-1) [3](#0-2) 

`init` accepts arbitrary `parameters` (participant set + threshold) and immediately transitions the contract to `Running` state with those parameters as the authoritative governance configuration: [4](#0-3) 

Critically, `init` also calls `TeeState::with_mocked_participant_attestations` for the supplied participants, meaning the attacker's injected participants receive mocked-valid TEE attestations automatically, bypassing the attestation gate that would otherwise prevent unverified nodes from participating: [5](#0-4) 

The deployment workflow confirms there is always a window between contract deployment and the `init` call: [6](#0-5) 

### Impact Explanation

An attacker who wins the race installs themselves as the sole participant with `threshold = 1`. From that point:

- They are the only recognized participant in `RunningContractState`, so all governance votes (`vote_add_domains`, `vote_new_parameters`, etc.) require only their approval.
- They can respond to any `sign` or `request_app_private_key` request with their own key material, producing signatures that the contract accepts as legitimate threshold signatures.
- Legitimate operators cannot call `init` again because state already exists; recovery requires a contract redeployment, which itself may be frontrunnable.

This satisfies **Critical: Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization** and **Critical: Bypass of threshold-signature requirements or unauthorized access to MPC key shares**.

### Likelihood Explanation

NEAR's mempool is public. The `init` call is broadcast as a plain transaction with no special timing protection. The attacker needs only to observe the pending `init` transaction and submit their own with a higher gas price (or equivalent priority mechanism). No privileged access, key material, or threshold collusion is required — a single unprivileged NEAR account suffices.

### Recommendation

Add `#[private]` to `init`, consistent with `init_running` and `migrate`:

```rust
#[handle_result]
#[private]          // ← add this
#[init]
pub fn init(
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
) -> Result<Self, Error> {
```

`#[private]` enforces that `predecessor_account_id == current_account_id`, so only the contract account itself (the deployer) can call `init`. This matches the documented deployment procedure where `init` is always signed by the contract account. [7](#0-6) 

### Proof of Concept

1. Attacker monitors the NEAR mempool for a transaction calling `init` on the newly deployed MPC contract address.
2. Attacker submits their own `init` transaction with `parameters` containing only their own account as the sole participant and `threshold = 1`, with higher gas priority.
3. Attacker's transaction executes first; `#[init]` sets state, so the legitimate operator's `init` panics with "state already exists."
4. The contract is now `Running` with the attacker as the only participant, holding mocked-valid TEE attestations.
5. Attacker calls `vote_add_domains` (requires only their single vote to reach threshold) to register signing domains.
6. Any user's `sign(...)` request is now answered exclusively by the attacker's node, which produces signatures under attacker-controlled key material — constituting unauthorized threshold signature issuance over the entire MPC network.

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

**File:** crates/contract/src/lib.rs (L1944-1945)
```rust
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

**File:** crates/contract/src/lib.rs (L1976-1985)
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
```

**File:** crates/contract/src/lib.rs (L2060-2063)
```rust
    #[private]
    #[init(ignore_state)]
    #[handle_result]
    pub fn migrate() -> Result<Self, Error> {
```

**File:** docs/localnet/localnet.md (L265-269)
```markdown
Now, we should be ready to call the `init` function on the contract.

```shell
near contract call-function as-transaction mpc-contract.test.near init file-args /tmp/init_args.json prepaid-gas '300.0 Tgas' attached-deposit '0 NEAR' sign-as mpc-contract.test.near network-config mpc-localnet sign-with-keychain send
```
```
