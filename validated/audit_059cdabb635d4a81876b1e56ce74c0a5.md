Confirmed: `TransferToGasKey` is grouped with `Action::CreateAccount(_) | Action::FunctionCall(_) | Action::Transfer(_)` in `check_actor_permissions` at [1](#0-0) , meaning it has no actor/ownership restriction — exactly like an ordinary `Transfer`, it can be sent by **any predecessor** to fund **any account's** gas key, as long as the target key exists. `action_transfer_to_gas_key` itself only checks that the key exists and is a gas key, then unconditionally adds `action.deposit` to `gas_key_info.balance` [2](#0-1) .

### Title
Unprivileged front-running of gas-key deletion via permissionless `TransferToGasKey` dust deposits - (File: runtime/runtime/src/access_keys.rs)

### Summary
Any account can call `TransferToGasKey` against another account's gas key at any time, with no ownership check. An attacker can watch the mempool for a `DeleteKey`/`DeleteAccount` transaction that relies on the gas key balance being at or below the `MAX_BALANCE_TO_BURN` threshold (1 NEAR), and front-run it with a minimal deposit that pushes the balance over the threshold, causing the legitimate deletion to fail deterministically.

### Finding Description
`delete_gas_key` (invoked from `action_delete_key`) and `action_delete_account` both reject the deletion if the gas key balance(s) exceed `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR): [3](#0-2) [4](#0-3) 

`GasKeyInfo::MAX_BALANCE_TO_BURN` is defined as a fixed 1 NEAR threshold: [5](#0-4) 

Crucially, `TransferToGasKey` has no actor/ownership restriction in `check_actor_permissions` — it is treated the same as a plain `Transfer`, so any predecessor (not just the key's owner) can top up any account's gas key balance: [1](#0-0) 

And `action_transfer_to_gas_key` performs no ownership check either — it merely verifies the key exists and is a gas key, then increments the balance by the attached deposit: [2](#0-1) 

This is structurally identical to the Ion-Protocol bug: a permissionless, cheap, threshold-crossing deposit made by an unrelated third party that deterministically causes a subsequent legitimate state-transition (`DeleteKey`/`DeleteAccount`) to fail, exactly as `repayBadDebt`/`liquidate`'s dependence on an externally-mutable value allowed griefing of `liquidate`.

### Impact Explanation
An attacker who observes a pending `DeleteKey` (for a gas key) or `DeleteAccount` transaction where the gas key balance sits near the 1 NEAR threshold can send a single, cheap `TransferToGasKey` receipt that nudges the balance above the limit. This causes the account owner's deletion transaction to fail with `GasKeyBalanceTooHigh`, forcing the victim to first issue a `WithdrawFromGasKey` to bring the balance back down before retrying deletion — and the attacker can repeat this griefing indefinitely and cheaply (deposit is fully recoverable by the victim via `WithdrawFromGasKey`, so this is a denial-of-service/griefing vector rather than fund theft, but it can block account deletion indefinitely for as long as the attacker chooses to grief). This is a low-cost, unprivileged DoS on a normal user action reachable via a standard transaction, not requiring any validator or node privilege.

### Likelihood Explanation
The griefing transaction (`TransferToGasKey`) is a standard, unprivileged action costing only the attached deposit (fully recoverable later by the account owner) plus gas fees, and can be triggered by watching the public mempool for `DeleteKey`/`DeleteAccount` transactions targeting accounts with gas keys near the threshold. No special access or validator status is required, making this easily and repeatedly exploitable by any observer.

### Recommendation
Restrict `TransferToGasKey` so that only the account itself (or an authorized access key holder for that account) can top up its own gas key balances, mirroring the actor check applied to sensitive mutations like `DeleteAccount`/`Stake`. Alternatively, decouple deletion eligibility from a balance value that a third party can mutate — e.g., snapshot/lock the balance at the time deletion is initiated, or make the burn-threshold check tolerant of races (e.g., burn only up to the threshold and refund excess) rather than hard-failing the whole deletion.

### Proof of Concept
1. Victim account `alice.near` has a gas key `pk` with balance `0.9 NEAR` (below `MAX_BALANCE_TO_BURN = 1 NEAR`).
2. Victim submits `DeleteKey { public_key: pk }` (or `DeleteAccountAction`) expecting it to succeed since `0.9 NEAR <= 1 NEAR`.
3. Attacker observes this transaction in the mempool and submits `TransferToGasKey { public_key: pk, deposit: 0.2 NEAR }` targeting `alice.near`'s gas key — no ownership check blocks this, per `action_transfer_to_gas_key` and `check_actor_permissions`.
4. If the attacker's receipt is applied before the victim's `DeleteKey`, `gas_key_info.balance` becomes `1.1 NEAR`, exceeding `MAX_BALANCE_TO_BURN`.
5. The victim's `DeleteKey`/`DeleteAccount` now fails with `ActionErrorKind::GasKeyBalanceTooHigh` per `delete_gas_key`/`action_delete_account`, confirmed by the existing test pattern `test_delete_account_gas_key_balance_at_threshold` which shows deletion behavior exactly at the boundary [6](#0-5) .

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

**File:** runtime/runtime/src/actions.rs (L777-784)
```rust
        Action::CreateAccount(_)
        | Action::FunctionCall(_)
        | Action::Transfer(_)
        | Action::TransferToGasKey(_) => (),
        Action::Delegate(_) | Action::DelegateV2(_) => (),
        Action::DeterministicStateInit(_) => (),
    };
    Ok(())
```

**File:** runtime/runtime/src/access_keys.rs (L102-111)
```rust
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

**File:** runtime/runtime/src/access_keys.rs (L1334-1368)
```rust
    #[test]
    fn test_delete_account_gas_key_balance_at_threshold() {
        let (account_id, public_key, access_key) = test_account_keys();
        let public_keys: Vec<PublicKey> = (0..3)
            .map(|i| PublicKey::from_seed(KeyType::ED25519, &format!("gas_key_{i}")))
            .collect();
        let mut state_update = setup_account(&account_id, &public_key, &access_key);
        let mut account = get_account(&state_update, &account_id).unwrap().unwrap();
        for public_key in &public_keys {
            add_gas_key_to_account(&mut state_update, &mut account, &account_id, public_key);
        }

        // Fund gas keys so total is exactly 1 NEAR
        let deposit_amounts = [
            Balance::from_millinear(400),
            Balance::from_millinear(400),
            Balance::from_millinear(200),
        ];
        for (pk, amount) in public_keys.iter().zip(deposit_amounts.iter()) {
            transfer_to_gas_key(&mut state_update, &account_id, pk, *amount);
        }
        state_update.commit(StateChangeCause::InitialState);

        let action_result = test_delete_account(
            &account_id,
            AccountContract::from_local_code_hash(CryptoHash::default()),
            100,
            PROTOCOL_VERSION,
            &mut state_update,
        );
        assert!(action_result.result.is_ok());
        let expected_burnt =
            deposit_amounts.iter().fold(Balance::ZERO, |acc, x| acc.checked_add(*x).unwrap());
        assert_eq!(action_result.tokens_burnt, expected_burnt);
    }
```

**File:** core/primitives-core/src/account.rs (L815-823)
```rust
impl GasKeyInfo {
    /// Maximum gas key balance that can be burned during key or account deletion.
    /// Deletion fails if the (sum of) gas key balance(s) exceeds this threshold.
    pub const MAX_BALANCE_TO_BURN: Balance = Balance::from_near(1);

    pub fn borsh_len() -> usize {
        borsh::object_length(&Self { balance: Balance::from_yoctonear(0), num_nonces: 0 }).unwrap()
    }
}
```
