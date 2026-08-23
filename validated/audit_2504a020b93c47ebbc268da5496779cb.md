Based on the codebase evidence gathered, I found a directly analogous griefing pattern in nearcore's gas-key mechanism.

### Title
Anyone can grief a gas key's deletion by funding it past the burn ceiling - (File: `runtime/runtime/src/access_keys.rs`)

### Summary
`TransferToGasKeyAction` lets an arbitrary predecessor add NEAR to any account's existing gas key balance, with no check that the caller is the account owner. Because `DeleteKeyAction`/`DeleteAccountAction` refuse to burn a gas key balance above `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR), an attacker can repeatedly "grief-fund" a target's gas key with tiny deposits to keep it above the ceiling, permanently blocking key/account deletion — the same pattern as the sandclock report, where anyone sending funds to a component keeps a balance check from ever being satisfied.

### Finding Description
`action_transfer_to_gas_key` only checks that the target `public_key` is a gas key on `account_id`; it takes no actor/signer identity as a parameter and performs no ownership check before crediting the deposit: [1](#0-0) 

This action is explicitly exposed to arbitrary receivers via the promise-batch host function, which lets a contract target any `account_id` in `promise_batch_create` and then append a `TransferToGasKey` action to that batch: [2](#0-1) 

It is also reachable directly as a top-level transaction action (`Action::TransferToGasKey`), whose struct doc confirms its purpose is simply "Transfer NEAR to a gas key's balance": [3](#0-2) 

The deletion paths then enforce a hard balance ceiling before allowing burn/removal — first for a single-key deletion: [4](#0-3) 

and again for the aggregate of all gas keys when deleting the whole account: [5](#0-4) 

The ceiling constant is fixed and small (1 NEAR): [6](#0-5) 

This mirrors the sandclock bug class exactly: an externally-triggerable balance top-up (anyone can send funds) feeds directly into a threshold check (`investedAssets() == 0` / `GasKeyBalanceTooHigh`) that gates a state-changing/cleanup action (`setStrategy` / `DeleteKey`, `DeleteAccount`). Since the top-up cost is trivial (as little as 1 yoctoNEAR) relative to the ceiling (1 NEAR) and the account owner cannot prevent others from crediting an existing gas key, the attacker can repeat the funding indefinitely, faster and cheaper than the victim can withdraw and delete.

### Impact Explanation
This is an unauthorized-state-change / griefing-DoS bug: an unprivileged attacker can force permanent (or costly-to-recover) unremovability of a victim's gas key or entire account, since `DeleteAccount` aggregates all gas key balances and fails outright if the total exceeds 1 NEAR. The victim is forced into a withdraw-then-immediately-race-to-delete loop that the attacker can keep breaking with a 1-yoctoNEAR transaction, at negligible attacker cost versus repeated victim gas expenditure. This blocks legitimate account cleanup, storage-staking refund, and access-key rotation — a real, unprivileged, on-chain-reachable denial of function that matches the accepted "unauthorized state change" / "underpriced execution" impact categories.

### Likelihood Explanation
High. `TransferToGasKeyAction` requires only knowledge of the target account's gas-key public key (public on-chain data, visible via `ViewAccessKeyList`/`ViewGasKeyNonces` RPCs) and a minimal token amount. No special privileges, access keys, or contract cooperation from the victim are needed — the action is directly submittable in a signed transaction or via a contract's promise batch, both of which are reachable from any submitted transaction.

### Recommendation
Do not allow unrestricted third-party crediting of a gas key balance past the point where it could exceed `GasKeyInfo::MAX_BALANCE_TO_BURN` combined with the account's intent to delete. Options:
- Restrict `TransferToGasKeyAction` to be performable only by the account owner (`actor_id == account_id`), consistent with `AddKey`/`DeleteKey`/self-only action semantics.
- Or decouple deletion from the gas key balance ceiling by giving the runtime a path to force-burn/refund the balance to the account (or beneficiary) rather than hard-failing `DeleteKey`/`DeleteAccount`, so a griefer cannot indefinitely block cleanup.

### Proof of Concept
1. Attacker observes on-chain that account `victim.near` has a gas key with public key `PK` and small balance (below 1 NEAR).
2. Attacker submits `SignedTransaction { signer: attacker.near, receiver: victim.near, actions: [TransferToGasKeyAction { public_key: PK, deposit: 1 yoctoNEAR }] }` (or the equivalent via `promise_batch_action_transfer_to_gas_key` from a contract), repeated as needed to push the gas key's balance above `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR): [6](#0-5) 
3. Victim (or anyone) attempts `DeleteKeyAction { public_key: PK }` or `DeleteAccountAction` on `victim.near`; the runtime returns `ActionErrorKind::GasKeyBalanceTooHigh` and refuses to delete, per: [4](#0-3)  and [7](#0-6) 
4. Even if the victim withdraws the balance via `WithdrawFromGasKeyAction`, the attacker can immediately resend step 2, repeating the denial indefinitely at negligible cost.

**Uncertainty**: I could not fully trace `action_validation.rs`/`verifier.rs` (limited to a single match each with no time left to inspect content) to conclusively rule out an actor-identity restriction on `TransferToGasKeyAction` at the top-level-transaction validation layer. The strongest evidence — the function signature of `action_transfer_to_gas_key` taking no actor parameter, and the existence of a promise-batch host function that targets an arbitrary `account_id` — strongly indicates no such restriction exists, but this should be explicitly confirmed against `verifier.rs`/`action_validation.rs` before treating this as fully proven.

### Citations

**File:** runtime/runtime/src/access_keys.rs (L93-111)
```rust
fn delete_gas_key(
    config: &RuntimeConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    result: &mut ActionResult,
    account_id: &AccountId,
    public_key: &PublicKey,
    access_key: &AccessKey,
    gas_key_info: &GasKeyInfo,
) -> Result<(), RuntimeError> {
    if gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN {
        result.result = Err(ActionErrorKind::GasKeyBalanceTooHigh {
            account_id: account_id.clone(),
            public_key: Some(Box::new(public_key.clone())),
            balance: gas_key_info.balance,
        }
        .into());
        return Ok(());
    }
```

**File:** runtime/runtime/src/access_keys.rs (L257-288)
```rust
pub(crate) fn action_transfer_to_gas_key(
    state_update: &mut TrieUpdate,
    result: &mut ActionResult,
    account_id: &AccountId,
    action: &TransferToGasKeyAction,
) -> Result<(), RuntimeError> {
    let Some(mut access_key) = get_access_key(state_update, account_id, &action.public_key)? else {
        result.result = Err(ActionErrorKind::GasKeyDoesNotExist {
            account_id: account_id.clone(),
            public_key: Box::new(action.public_key.clone()),
        }
        .into());
        return Ok(());
    };
    let Some(gas_key_info) = access_key.gas_key_info_mut() else {
        // Key exists but is not a gas key
        result.result = Err(ActionErrorKind::GasKeyDoesNotExist {
            account_id: account_id.clone(),
            public_key: Box::new(action.public_key.clone()),
        }
        .into());
        return Ok(());
    };

    gas_key_info.balance = gas_key_info.balance.checked_add(action.deposit).ok_or_else(|| {
        RuntimeError::StorageError(StorageError::StorageInconsistentState(
            "gas key balance integer overflow".to_string(),
        ))
    })?;
    set_access_key(state_update, account_id.clone(), action.public_key.clone(), &access_key);
    Ok(())
}
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/logic.rs (L3297-3343)
```rust
pub fn promise_batch_action_transfer_to_gas_key(
    ctx: &mut Ctx,
    memory: &mut [u8],
    promise_idx: u64,
    public_key_len: u64,
    public_key_ptr: u64,
    amount_ptr: u64,
) -> Result<()> {
    ctx.result_state.gas_counter.pay_base(base)?;
    if ctx.context.is_view() {
        return Err(HostError::ProhibitedInView {
            method_name: "promise_batch_action_transfer_to_gas_key".to_string(),
        }
        .into());
    }
    let public_key = get_public_key(
        &mut ctx.result_state.gas_counter,
        memory,
        &ctx.registers,
        public_key_ptr,
        public_key_len,
    )?;
    let amount =
        Balance::from_yoctonear(get_u128(&mut ctx.result_state.gas_counter, memory, amount_ptr)?);
    let (receipt_idx, sir) = promise_idx_to_receipt_idx_with_sir(ctx, promise_idx)?;
    let receiver_id = ctx.ext.get_receipt_receiver(receipt_idx);
    let send = gas_key_transfer_send_fee(&ctx.fees_config, sir, public_key_len as usize);
    let exec =
        gas_key_transfer_exec_fee(&ctx.fees_config, receiver_id.len(), public_key_len as usize);
    let burn_base = send.base;
    let use_base = burn_base.gas.checked_add(exec.base.gas).ok_or(HostError::IntegerOverflow)?;
    ctx.result_state.gas_counter.pay_action_accumulated(
        burn_base,
        use_base,
        ActionCosts::gas_key_transfer_base,
    )?;
    let burn_byte = send.per_byte;
    let use_byte =
        burn_byte.gas.checked_add(exec.per_byte.gas).ok_or(HostError::IntegerOverflow)?;
    ctx.result_state.gas_counter.pay_action_accumulated(
        burn_byte,
        use_byte,
        ActionCosts::gas_key_byte,
    )?;
    ctx.result_state.deduct_balance(amount)?;
    ctx.ext.append_action_transfer_to_gas_key(receipt_idx, public_key.decode()?, amount);
    Ok(())
```

**File:** core/primitives/src/action/mod.rs (L291-309)
```rust
/// Transfer NEAR to a gas key's balance
#[derive(
    BorshSerialize,
    BorshDeserialize,
    PartialEq,
    Eq,
    Clone,
    Debug,
    serde::Serialize,
    serde::Deserialize,
    ProtocolSchema,
)]
#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
pub struct TransferToGasKeyAction {
    /// The public key of the gas key to fund
    pub public_key: PublicKey,
    /// Amount of NEAR to transfer to the gas key
    pub deposit: Balance,
}
```

**File:** runtime/runtime/src/actions.rs (L333-348)
```rust
    if account_storage_usage > Account::MAX_ACCOUNT_DELETION_STORAGE_USAGE {
        result.result =
            Err(ActionErrorKind::DeleteAccountWithLargeState { account_id: account_id.clone() }
                .into());
        return Ok(());
    }
    let gas_key_balance_to_burn = compute_gas_key_balance_sum(state_update, account_id)?;
    if gas_key_balance_to_burn > GasKeyInfo::MAX_BALANCE_TO_BURN {
        result.result = Err(ActionErrorKind::GasKeyBalanceTooHigh {
            account_id: account_id.clone(),
            public_key: None,
            balance: gas_key_balance_to_burn,
        }
        .into());
        return Ok(());
    }
```

**File:** core/primitives-core/src/account.rs (L551-554)
```rust
impl GasKeyInfo {
    /// Maximum gas key balance that can be burned during key or account deletion.
    /// Deletion fails if the (sum of) gas key balance(s) exceeds this threshold.
    pub const MAX_BALANCE_TO_BURN: Balance = Balance::from_near(1);
```
