### Title
Unprivileged `TransferToGasKey` Manipulation Causes Permanent `DeleteKey` DoS on Victim Gas Keys - (File: runtime/runtime/src/access_keys.rs)

### Summary
Any unprivileged account can fund a victim's gas key above the `GasKeyInfo::MAX_BALANCE_TO_BURN` threshold (1 NEAR) by sending a `TransferToGasKey` action targeting the victim's account. Once the gas key balance exceeds this threshold, the `delete_gas_key` function unconditionally rejects any `DeleteKey` action on that key with `GasKeyBalanceTooHigh`. An attacker can maintain this state indefinitely by front-running every victim `WithdrawFromGasKey` transaction, permanently denying the victim the ability to delete a potentially compromised gas key.

### Finding Description

`action_transfer_to_gas_key` in `runtime/runtime/src/access_keys.rs` imposes no restriction on who may fund a gas key — any account can send a transaction with `receiver_id = victim_account` and `Action::TransferToGasKey { public_key: victim_gas_key_pk, deposit: X }`. The deposit is deducted from the attacker's balance and credited to the victim's gas key balance in trie state. [1](#0-0) 

When the victim subsequently submits a `DeleteKey` action, `delete_gas_key` checks:

```rust
if gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN {
    result.result = Err(ActionErrorKind::GasKeyBalanceTooHigh { ... });
    return Ok(());
}
``` [2](#0-1) 

`MAX_BALANCE_TO_BURN` is exactly 1 NEAR: [3](#0-2) 

The attacker's entry path requires no special privilege: a standard signed transaction with `receiver_id = victim` and `Action::TransferToGasKey` is sufficient. The same effect is achievable from a deployed contract via the `promise_batch_action_transfer_to_gas_key` host function: [4](#0-3) 

The victim's only recourse is `WithdrawFromGasKey`, but this action is only available via transactions (no host function exists for it), and the attacker can front-run each withdrawal with a new `TransferToGasKey` to restore the balance above the threshold. [5](#0-4) 

### Impact Explanation

The corrupted protocol value is `gas_key_info.balance` in the trie state for the victim's gas key. Once pushed above 1 NEAR, every `DeleteKey` action on that key produces `ActionErrorKind::GasKeyBalanceTooHigh` and the key is not removed from state. If the victim's gas key is compromised (its private key is leaked), the attacker can prevent the victim from revoking it indefinitely, keeping the compromised key active. The gas key remains usable for transactions by whoever holds the private key, meaning the attacker (if they also hold the key) can continue signing transactions on the victim's behalf while the victim cannot revoke access.

The corrupted DB entry is the `AccessKey` trie entry for `(victim_account_id, gas_key_public_key)`, specifically its `GasKeyInfo::balance` field.

### Likelihood Explanation

The attack is cheap and straightforward. The attacker sends a single transaction with `receiver_id = victim_account`, `Action::TransferToGasKey { public_key: victim_gas_key_pk, deposit: 1 NEAR + 1 yoctoNEAR }`. The cost is approximately 1 NEAR plus transaction fees. The NEAR tokens are not lost — they are credited to the victim's gas key balance and can be withdrawn by the victim — but the attacker can repeat the funding after each victim withdrawal, sustaining the DoS at the cost of only gas fees per round. No validator, node admin, or trusted-service privilege is required.

### Recommendation

1. **Remove the `MAX_BALANCE_TO_BURN` hard block on `DeleteKey`**: Instead of rejecting deletion when the balance exceeds 1 NEAR, burn the balance unconditionally (or up to a higher limit), or automatically refund the excess to the account owner before deletion.
2. **Alternatively, restrict who can fund a gas key**: Require that `TransferToGasKey` actions can only be sent by the account that owns the gas key (i.e., `signer_id == receiver_id`), preventing third-party funding.
3. **Or add an atomic withdraw-and-delete operation**: Allow the owner to atomically withdraw the full balance and delete the key in a single receipt, eliminating the front-running window.

### Proof of Concept

1. Victim `alice.near` has gas key `GK` with balance 0.5 NEAR.
2. Attacker sends:
   ```
   Transaction {
     signer_id: "attacker.near",
     receiver_id: "alice.near",
     actions: [TransferToGasKey { public_key: GK, deposit: 0.6 NEAR }]
   }
   ```
3. `action_transfer_to_gas_key` credits 0.6 NEAR to `GK.balance`, making it 1.1 NEAR. [6](#0-5) 
4. Alice submits `DeleteKey { public_key: GK }`. The runtime calls `delete_gas_key`, which checks `1.1 NEAR > MAX_BALANCE_TO_BURN (1 NEAR)` → returns `GasKeyBalanceTooHigh`. Key is not deleted. [7](#0-6) 
5. Alice submits `WithdrawFromGasKey { public_key: GK, amount: 0.2 NEAR }` to reduce balance to 0.9 NEAR.
6. Attacker front-runs or immediately follows with another `TransferToGasKey { deposit: 0.2 NEAR }`, restoring balance to 1.1 NEAR.
7. Steps 4–6 repeat indefinitely. Alice cannot delete `GK`.

### Citations

**File:** runtime/runtime/src/access_keys.rs (L103-111)
```rust
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

**File:** runtime/runtime/src/access_keys.rs (L257-287)
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
```

**File:** runtime/runtime/src/access_keys.rs (L290-335)
```rust
pub(crate) fn action_withdraw_from_gas_key(
    state_update: &mut TrieUpdate,
    account: &mut Account,
    result: &mut ActionResult,
    account_id: &AccountId,
    action: &WithdrawFromGasKeyAction,
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

    let Some(updated_balance) = gas_key_info.balance.checked_sub(action.amount) else {
        result.result = Err(ActionErrorKind::InsufficientGasKeyBalance {
            account_id: account_id.clone(),
            public_key: Box::new(action.public_key.clone()),
            balance: gas_key_info.balance,
            required: action.amount,
        }
        .into());
        return Ok(());
    };
    gas_key_info.balance = updated_balance;
    set_access_key(state_update, account_id.clone(), action.public_key.clone(), &access_key);

    let new_account_balance = account.amount().checked_add(action.amount).ok_or_else(|| {
        RuntimeError::StorageError(StorageError::StorageInconsistentState(
            "Account balance integer overflow".to_string(),
        ))
    })?;
    account.set_amount(new_account_balance);
    Ok(())
}
```

**File:** core/primitives-core/src/account.rs (L551-554)
```rust
impl GasKeyInfo {
    /// Maximum gas key balance that can be burned during key or account deletion.
    /// Deletion fails if the (sum of) gas key balance(s) exceeds this threshold.
    pub const MAX_BALANCE_TO_BURN: Balance = Balance::from_near(1);
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L3071-3115)
```rust
    pub fn promise_batch_action_transfer_to_gas_key(
        &mut self,
        promise_idx: u64,
        public_key_len: u64,
        public_key_ptr: u64,
        amount_ptr: u64,
    ) -> Result<()> {
        self.result_state.gas_counter.pay_base(base)?;
        if self.context.is_view() {
            return Err(HostError::ProhibitedInView {
                method_name: "promise_batch_action_transfer_to_gas_key".to_string(),
            }
            .into());
        }
        let public_key = self.get_public_key(public_key_ptr, public_key_len)?;
        let amount = Balance::from_yoctonear(
            self.memory.get_u128(&mut self.result_state.gas_counter, amount_ptr)?,
        );
        let (receipt_idx, sir) = self.promise_idx_to_receipt_idx_with_sir(promise_idx)?;
        let receiver_id = self.ext.get_receipt_receiver(receipt_idx);
        let send = gas_key_transfer_send_fee(&self.fees_config, sir, public_key_len as usize);
        let exec = gas_key_transfer_exec_fee(
            &self.fees_config,
            receiver_id.len(),
            public_key_len as usize,
        );
        let burn_base = send.base;
        let use_base =
            burn_base.gas.checked_add(exec.base.gas).ok_or(HostError::IntegerOverflow)?;
        self.result_state.gas_counter.pay_action_accumulated(
            burn_base,
            use_base,
            ActionCosts::gas_key_transfer_base,
        )?;
        let burn_byte = send.per_byte;
        let use_byte =
            burn_byte.gas.checked_add(exec.per_byte.gas).ok_or(HostError::IntegerOverflow)?;
        self.result_state.gas_counter.pay_action_accumulated(
            burn_byte,
            use_byte,
            ActionCosts::gas_key_byte,
        )?;
        self.result_state.deduct_balance(amount)?;
        self.ext.append_action_transfer_to_gas_key(receipt_idx, public_key.decode()?, amount);
        Ok(())
```
