Found the critical fact: `check_actor_permissions` explicitly places `Action::TransferToGasKey(_)` in the **unrestricted** bucket alongside `CreateAccount`/`FunctionCall`/`Transfer` — it does **not** require `actor_id == account_id`, unlike `AddKey`/`DeleteKey`/`Stake`/`DeployContract`/`WithdrawFromGasKey`/`DeleteAccount` which do enforce that self-only check. [1](#0-0) 

This means **any account** can send a receipt containing a `TransferToGasKey` action targeting **any other account's** gas key (as long as the public key exists on that account), funding its `GasKeyInfo.balance` arbitrarily — exactly the "unprivileged third party pushes value into a target's balance-gated field" primitive from the KelpDAO bug (front-running an admin-gated removal by inflating a balance the removal logic checks). Whether this can *actually block* another privileged action the way the KelpDAO bug blocks `removeNodeDelegatorContractFromQueue` depends on where that inflated gas-key balance is later checked against a threshold:

- `delete_gas_key` (triggered by `DeleteKey`, a *self-only* action) rejects with `GasKeyBalanceTooHigh` if `gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR). [2](#0-1) 
- `action_delete_account` sums all gas-key balances via `compute_gas_key_balance_sum` and rejects the entire account deletion with the same `GasKeyBalanceTooHigh` error if the sum exceeds `MAX_BALANCE_TO_BURN`. [3](#0-2) 

So the reachable analog is: an unprivileged attacker sends a `TransferToGasKey` action (deposit > 1 NEAR, or enough to push the account's total gas-key balance over `MAX_BALANCE_TO_BURN`) targeting a victim account's existing gas key. This is not gated by `check_actor_permissions` (only `WithdrawFromGasKey`, not `TransferToGasKey`, is restricted to `actor_id == account_id`), so it succeeds even though the victim never asked to receive it. The victim's subsequent, otherwise-legitimate attempt to delete that gas key (`DeleteKey`) or delete the whole account (`DeleteAccount`) — both of which *are* self-only, privileged-by-key-ownership actions — will then fail with `GasKeyBalanceTooHigh`, since deletion refuses to proceed while `balance > 1 NEAR` (the code explicitly burns rather than refunds this balance, so it can't just be swept away). [4](#0-3) 

This matches the bug class precisely: an external, unprivileged party manipulates a balance field that a later privileged/self-authorized removal operation checks, causing that removal to revert/fail (DoS on `DeleteKey`/`DeleteAccount`) until the account owner manually works around it (e.g., by withdrawing/burning down the balance first via `WithdrawFromGasKey`, which the owner does control) — though note the owner does have a mitigation path here (`WithdrawFromGasKey` is self-only and can reduce the balance below the threshold), so this is a **griefing/inconvenience** DoS rather than a permanent block, similar in severity class to the medium-risk classification in the original report.

### Title
Unauthorized `TransferToGasKey` action lets any account grief another account's gas-key/account deletion — (File: `runtime/runtime/src/actions.rs`)

### Summary
`check_actor_permissions` restricts `AddKey`, `DeleteKey`, `Stake`, `DeployContract`, `WithdrawFromGasKey`, and `DeleteAccount` to `actor_id == account_id` (self-only), but deliberately omits `TransferToGasKey` from this restriction, grouping it with unrestricted actions like `Transfer` and `FunctionCall`. [1](#0-0) 

### Finding Description
`action_transfer_to_gas_key` looks up the gas key by `(account_id, public_key)` and increments `GasKeyInfo.balance` by the attached deposit, with no check on who the predecessor/sender is. [5](#0-4) 
Because `check_actor_permissions` does not gate `TransferToGasKey` on `actor_id == account_id`, an attacker can dispatch a receipt containing this action toward a victim's account, funding any of that account's (necessarily public, since it must be discoverable to target) gas keys past `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR). [6](#0-5) 
Later, when the account owner tries to delete that gas key or the whole account — both privileged, self-only operations — `delete_gas_key` and `action_delete_account` reject the operation with `GasKeyBalanceTooHigh` if the balance (or the account-wide sum) exceeds the 1 NEAR cap, because that balance is burned (not refunded) on deletion and the protocol caps how much can be burned this way. [7](#0-6) [3](#0-2) 

### Impact Explanation
This is analogous to the KelpDAO front-running bug: an unprivileged third party manipulates a balance field checked by a subsequent, otherwise-authorized state-changing operation, causing that operation to revert. Here it blocks `DeleteKey` on a gas key and/or `DeleteAccount` for the targeted account, until the owner takes remedial action.

### Likelihood Explanation
Low cost to an attacker: it only requires knowing a target's gas-key public key (discoverable via RPC `view_access_key_list`/similar) and sending >1 NEAR in a single `TransferToGasKey` action, or several to cross the aggregate threshold checked at account deletion. No special privilege or validator/network position is needed — reachable purely via a submitted transaction/receipt.

### Recommendation
Add `Action::TransferToGasKey(_)` to the `actor_id == account_id` branch in `check_actor_permissions` (alongside `WithdrawFromGasKey`), so only the account itself can fund its own gas keys, matching the intended self-only semantics of the rest of the gas-key management actions.

### Proof of Concept
1. Victim account `victim.near` has a gas key `pk_gas` with `balance = 0`.
2. Attacker `attacker.near` sends a transaction/receipt with a single `Action::TransferToGasKey(TransferToGasKeyAction { public_key: pk_gas, deposit: 2 NEAR })` addressed to `victim.near` (predecessor `attacker.near`, receiver `victim.near`).
3. `check_actor_permissions` allows it because `TransferToGasKey` is not in the self-only match arm. [8](#0-7) 
4. `action_transfer_to_gas_key` sets `gas_key_info.balance = 2 NEAR` on `victim.near`'s key, funded entirely by the attacker's own deposit. [9](#0-8) 
5. `victim.near` later signs a `DeleteKey` for `pk_gas` (self-only, authorized) — `delete_gas_key` now sees `balance (2 NEAR) > MAX_BALANCE_TO_BURN (1 NEAR)` and returns `GasKeyBalanceTooHigh`, blocking deletion. [10](#0-9) 
6. Similarly, a `DeleteAccount` on `victim.near` fails the same way if the aggregate gas-key balance exceeds the cap. [3](#0-2)

### Citations

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

**File:** runtime/runtime/src/actions.rs (L739-785)
```rust
pub(crate) fn check_actor_permissions(
    action: &Action,
    account: &Option<Account>,
    actor_id: &AccountId,
    account_id: &AccountId,
) -> Result<(), ActionError> {
    match action {
        Action::DeployContract(_)
        | Action::Stake(_)
        | Action::AddKey(_)
        | Action::DeleteKey(_)
        | Action::DeployGlobalContract(_)
        | Action::UseGlobalContract(_)
        | Action::WithdrawFromGasKey(_) => {
            if actor_id != account_id {
                return Err(ActionErrorKind::ActorNoPermission {
                    account_id: account_id.clone(),
                    actor_id: actor_id.clone(),
                }
                .into());
            }
        }
        Action::DeleteAccount(_) => {
            if actor_id != account_id {
                return Err(ActionErrorKind::ActorNoPermission {
                    account_id: account_id.clone(),
                    actor_id: actor_id.clone(),
                }
                .into());
            }
            let account = account.as_ref().unwrap();
            if !account.locked().is_zero() {
                return Err(ActionErrorKind::DeleteAccountStaking {
                    account_id: account_id.clone(),
                }
                .into());
            }
        }
        Action::CreateAccount(_)
        | Action::FunctionCall(_)
        | Action::Transfer(_)
        | Action::TransferToGasKey(_) => (),
        Action::Delegate(_) | Action::DelegateV2(_) => (),
        Action::DeterministicStateInit(_) => (),
    };
    Ok(())
}
```

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

**File:** protocol-model/spec/accounts-keys.md (L19-19)
```markdown
- **`GasKeyInfo`** — `core/primitives-core/src/account.rs:546` — `{ balance: Balance, num_nonces: NonceIndex }`. `balance` is a prepaid pot used to pay gas; `num_nonces` is the count of independent nonce slots. `MAX_BALANCE_TO_BURN = 1 NEAR` (`:554`) caps the balance that may be burned when deleting the key/account.
```

**File:** protocol-model/spec/accounts-keys.md (L46-46)
```markdown
- **Gas key** (`delete_gas_key`, `:93`): if `balance > MAX_BALANCE_TO_BURN` (1 NEAR) it errors `GasKeyBalanceTooHigh` and leaves the key intact (`:103`); otherwise it adds the balance to `result.tokens_burnt` (the prepaid pot is **burned**, not refunded, `:112`), removes every nonce entry, charges removal compute, removes the access key, and `saturating_sub`s the gas-key storage cost.
```
