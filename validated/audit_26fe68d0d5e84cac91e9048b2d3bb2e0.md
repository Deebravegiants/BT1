### Title
Anyone can permanently block a gas key's `DeleteKey`/`DeleteAccount` by topping-up its balance above the burn threshold - ([File: runtime/runtime/src/access_keys.rs](https://github.com/AYontt/nearcore--009/blob/main/runtime/runtime/src/access_keys.rs))

### Summary
`action_delete_key`/`action_delete_account` refuse to delete a gas key (or an account holding one) once the gas key's `balance` exceeds `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR), because the deletion path burns the balance rather than refunding it and caps how much can be silently burned. `action_transfer_to_gas_key`, which increases that balance, only requires knowing the target account id and the (public, on-chain) public key of an existing gas key — it does not require the caller to be the account owner. This mirrors the reported Solidity bug class: a "must be at/below threshold" guard that gates a legitimate/necessary state transition can be griefed by any unprivileged party topping up the guarded value.

### Finding Description
`action_transfer_to_gas_key` looks up the access key on `account_id` and adds `action.deposit` to `gas_key_info.balance`, with no check that the transaction/receipt predecessor is the account itself: [1](#0-0) 

That balance is later checked by `delete_gas_key` (invoked from `action_delete_key`) — if `gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN`, deletion of that specific key fails with `GasKeyBalanceTooHigh`: [2](#0-1) 

`action_delete_account` performs the analogous aggregate check across all gas keys on the account before allowing the whole account to be deleted: [3](#0-2) 

The doc/spec explicitly frames this as a hard invariant tied to `MAX_BALANCE_TO_BURN`, described as bounding the "burn" that occurs on deletion: [4](#0-3) 

Public keys of existing gas keys are visible on-chain (via `view_access_key`/state), so any account can construct a transaction/receipt targeting a victim account with a `TransferToGasKeyAction` naming that public key and a deposit that, combined with the victim's existing gas-key balance, pushes the total over `MAX_BALANCE_TO_BURN`. Because the check compares against a fixed threshold rather than "was this specific over-threshold balance intentionally accepted by the owner," the attacker only needs to spend the delta needed to cross the threshold (analogous to the 1-wei griefing in the original report) to permanently block the victim from deleting that key, or — since `action_delete_account` sums balances across all gas keys — from deleting the whole account.

### Impact Explanation
An attacker can, for the cost of a small transfer, deny a victim account the ability to delete a specific gas key or (if it tips the aggregate sum) the entire account, forcing the victim either to leave the key/account permanently un-deletable or to accept burning up to 1 NEAR of their own funds to work around the block. This is a denial-of-service against normal account/key lifecycle operations triggered purely by an unprivileged transaction.

### Likelihood Explanation
Likelihood is high in principle: the target public key is public information, `TransferToGasKeyAction` execution shows no ownership/self-only check in the action handler itself, and the amount needed to cross the fixed 1 NEAR threshold can be minimal if the victim's gas key already holds a balance close to it. The main residual uncertainty is whether `verifier.rs` (which references `TransferToGasKey` in three places not fully inspected here) imposes an additional self-only restriction at validation time before the action reaches `access_keys.rs`; that could not be conclusively confirmed with the available context.

### Recommendation
- Confirm in `runtime/runtime/src/verifier.rs` whether `TransferToGasKeyAction` is restricted to same-account (`predecessor_id == receiver_id`) receipts; if not, add that restriction so only the account itself can fund its own gas keys.
- Alternatively, decouple the deletion-blocking threshold from attacker-controllable inputs, e.g., refund/burn any balance at deletion time regardless of size (removing the `GasKeyBalanceTooHigh` hard failure), or cap `TransferToGasKeyAction` deposits per call/account so no third party can push a key past the burn threshold without the owner's consent.

### Proof of Concept
1. Query the victim account's existing gas key public key via `view_access_key` (public state).
2. Attacker submits a transaction/receipt: `signer_id = attacker`, `receiver_id = victim`, `actions = [TransferToGasKeyAction { public_key: victim_gas_key, deposit: X }]`, where `X` is chosen so `victim_gas_key.balance + X > GasKeyInfo::MAX_BALANCE_TO_BURN` (per `runtime/runtime/src/access_keys.rs:103` / `runtime/runtime/src/actions.rs:355`).
3. Victim subsequently attempts `DeleteKey` on that key or `DeleteAccount`; both fail with `GasKeyBalanceTooHigh` (`runtime/runtime/src/access_keys.rs:104-109`, `runtime/runtime/src/actions.rs:356-362`), permanently blocking the operation unless the victim accepts burning funds.

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

**File:** runtime/runtime/src/actions.rs (L354-363)
```rust
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

**File:** protocol-model/spec/accounts-keys.md (L108-109)
```markdown
- **Storage stake backs storage usage** unless zero-balance: `check_storage_stake` (`verifier.rs:48`); violation → `LackBalanceForStorageStaking`/`LackBalanceForState`. An arithmetic-overflow inconsistency (`storage_amount_per_byte * storage_usage` or `amount + locked` overflows, `verifier.rs:56`,`:65`) returns `StorageStakingError::StorageError`, surfaced as `StorageInconsistentState`.
- **Gas-key deletion burns ≤ 1 NEAR**: `delete_gas_key` errors `GasKeyBalanceTooHigh` and aborts if `balance > MAX_BALANCE_TO_BURN`; otherwise the balance is burned (added to `tokens_burnt`, not refunded) (`access_keys.rs:103`,`:112`). Account deletion sums all gas-key balances against the same threshold (`actions.rs:389`, asserted by `test_delete_account_gas_key_balance_too_high`).
```
