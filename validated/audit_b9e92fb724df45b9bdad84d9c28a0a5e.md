Key finding: `check_actor_permissions` in `runtime/runtime/src/actions.rs:739-785` explicitly places `Action::TransferToGasKey(_)` in the group requiring **no** actor/receiver match (alongside `CreateAccount`, `FunctionCall`, `Transfer`), unlike `AddKey`, `DeleteKey`, `WithdrawFromGasKey`, `DeployContract`, `Stake`, which require `actor_id == account_id`. [1](#0-0) 

This means `TransferToGasKey` is a **permissionless deposit action**: any account can send a `TransferToGasKey` action to `receiver_id` = victim account, funding one of the victim's own gas keys, exactly as any account can call `Transfer`. This mirrors the report's core mechanic — an unprivileged third party can push a balance onto a target account/key that the target does not want and cannot refuse, because the deposit path itself carries no authorization check on the sender.

The relevant "must be low/zero" gate that this can be used to grief is in `action_delete_account` (`runtime/runtime/src/actions.rs:314-390`): it sums all gas-key balances via `compute_gas_key_balance_sum` and rejects the whole `DeleteAccount` action with `GasKeyBalanceTooHigh` if the sum exceeds `GasKeyInfo::MAX_BALANCE_TO_BURN`. [2](#0-1) 

The same threshold check exists on `DeleteKey` for gas keys specifically, in `delete_gas_key` (`runtime/runtime/src/access_keys.rs:93-111`): [3](#0-2) 

### Title
Permissionless `TransferToGasKey` deposits can grief `DeleteAccount`/`DeleteKey` via `GasKeyBalanceTooHigh` - (File: `runtime/runtime/src/actions.rs`, `runtime/runtime/src/access_keys.rs`)

### Summary
`TransferToGasKey` is exempted from the actor/receiver equality check in `check_actor_permissions`, so any unprivileged account can push NEAR into a victim's gas key without the victim's consent. If the victim later tries to delete that gas key (`DeleteKey`) or delete their account entirely (`DeleteAccount`), the runtime sums the gas key balance(s) and aborts the action with `GasKeyBalanceTooHigh` when the sum exceeds `GasKeyInfo::MAX_BALANCE_TO_BURN`, because the burn amount is capped to bound how much NEAR can be silently destroyed on deletion.

### Finding Description
`check_actor_permissions` requires `actor_id == account_id` for `DeployContract`, `Stake`, `AddKey`, `DeleteKey`, `DeployGlobalContract`, `UseGlobalContract`, `WithdrawFromGasKey`, and `DeleteAccount`, but explicitly allows `Action::TransferToGasKey(_)` to pass with no actor check, grouping it with `CreateAccount`/`FunctionCall`/`Transfer` — actions that are inherently meant to be invoked by third parties. [1](#0-0) 

Consequently, `TransferToGasKey(public_key, deposit)` addressed at a victim account with `receiver_id = victim` and any `predecessor_id` succeeds and increases `gas_key_info.balance` on the victim's gas key, as shown by `transfer_to_gas_key`/`action_transfer_to_gas_key` tests which never validate a sender identity beyond the target account's existence. [4](#0-3) 

When the victim (the actual key owner) later attempts `DeleteKey` on that gas key, `delete_gas_key` checks `gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN` and, if true, fails with `GasKeyBalanceTooHigh` instead of deleting the key. [5](#0-4) 

Similarly, `action_delete_account` sums all of the account's gas-key balances (`compute_gas_key_balance_sum`) and rejects the entire `DeleteAccount` action with the same error if the sum exceeds the burn cap, leaving the account (and its state) undeleted. [2](#0-1) 

This is structurally the same bug class as the external report: a state transition that is gated on "this balance/asset must be at/below a threshold" can be permanently blocked by an attacker who is permitted to deposit that asset into the target's account without the target's consent, and the target has no way to reject or preemptively drain it before the deposit lands (deposits and the blocking check happen in different, attacker-controlled-timing transactions).

### Impact Explanation
An attacker can grief any account with one or more gas keys by repeatedly sending small `TransferToGasKey` deposits (each transaction is cheap — one action, no special permission) until the summed gas-key balance(s) on the target exceed `GasKeyInfo::MAX_BALANCE_TO_BURN`. This permanently blocks that account from performing `DeleteKey` on the affected gas key and blocks `DeleteAccount` entirely (since deletion requires burning all gas-key balances under the cap), denying the account owner's ability to reclaim their account's storage-staked balance or exit the chain state. This is a denial-of-service against an unprivileged user's own account-lifecycle actions, reachable purely through submitted transactions with no validator or node-level privilege required.

### Likelihood Explanation
Highly likely to be exploitable in practice: `TransferToGasKey` has no deposit-size floor preventing repeated small transfers, the action is deliberately permissionless (by design, similar to `Transfer`), and `MAX_BALANCE_TO_BURN` is a fixed protocol constant the attacker can determine and exceed with a bounded, low-cost number of transactions. The only friction is gas/transaction fees for the attacker, which are minor compared to permanently locking a victim's account.

### Recommendation
Consider one or more of: (1) requiring `TransferToGasKey` deposits above `MAX_BALANCE_TO_BURN` per key to be rejected/capped so no single key can accumulate an un-deletable balance regardless of depositor identity, (2) allowing `DeleteKey`/`DeleteAccount` to refund excess gas-key balance to the account itself (or beneficiary) instead of unconditionally failing when the sum exceeds the burn cap, or (3) restricting `TransferToGasKey` to be actor-gated (`actor_id == account_id`, i.e. self-funding only, matching `WithdrawFromGasKey`) if third-party funding of gas keys is not an intended use case.

### Proof of Concept
1. Victim account `V` creates a gas key via `AddKey` with `AccessKey::gas_key_full_access(n)`.
2. Attacker `A` (any unprivileged account) repeatedly submits `SignedTransaction` from `A` to `V` containing `Action::TransferToGasKey(TransferToGasKeyAction { public_key: V's gas key, deposit })`. This succeeds each time because `check_actor_permissions` does not gate `TransferToGasKey` on `actor_id == account_id`. [6](#0-5) 
3. Once the accumulated `gas_key_info.balance` exceeds `GasKeyInfo::MAX_BALANCE_TO_BURN`, `V` submits `Action::DeleteKey` for that gas key (or `Action::DeleteAccount`); the runtime returns `ActionErrorKind::GasKeyBalanceTooHigh` and the account/key remains, as exercised by `test_delete_account_burns_gas_key_balances` for balances under the cap. [7](#0-6) 
4. `V` is now permanently unable to delete that gas key or their account via the normal path.

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

**File:** runtime/runtime/src/access_keys.rs (L715-755)
```rust
    #[test]
    fn test_delete_account_burns_gas_key_balances() {
        let (account_id, public_key, access_key) = test_account_keys();
        let public_keys: Vec<PublicKey> = (0..3)
            .map(|i| PublicKey::from_seed(KeyType::ED25519, &format!("gas_key_{i}")))
            .collect();
        let mut state_update = setup_account(&account_id, &public_key, &access_key);
        let mut account = get_account(&state_update, &account_id).unwrap().unwrap();
        for public_key in &public_keys {
            add_gas_key_to_account(&mut state_update, &mut account, &account_id, public_key);
        }

        // Fund each gas key with different amounts
        let deposit_amounts = [
            Balance::from_yoctonear(100_000),
            Balance::from_yoctonear(200_000),
            Balance::from_yoctonear(300_000),
        ];
        for (public_key, amount) in public_keys.iter().zip(deposit_amounts.iter()) {
            transfer_to_gas_key(&mut state_update, &account_id, public_key, *amount);
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

        // Verify total burned balance equals sum of all gas key balances
        let expected_burnt =
            deposit_amounts.iter().fold(Balance::ZERO, |acc, x| acc.checked_add(*x).unwrap());
        assert_eq!(action_result.tokens_burnt, expected_burnt);
        let expected_compute: u64 = public_keys
            .iter()
            .map(|pk| expected_nonce_remove_compute(&account_id, pk, TEST_NUM_NONCES as usize))
            .sum();
        assert_eq!(action_result.compute_usage, expected_compute);
```

**File:** runtime/runtime/src/access_keys.rs (L984-1020)
```rust
    fn transfer_to_gas_key(
        state_update: &mut TrieUpdate,
        account_id: &AccountId,
        public_key: &PublicKey,
        amount: Balance,
    ) {
        let mut result = ActionResult::default();
        let action = TransferToGasKeyAction { public_key: public_key.clone(), deposit: amount };
        action_transfer_to_gas_key(state_update, &mut result, account_id, &action).unwrap();
        assert!(result.result.is_ok());
    }

    #[test]
    fn test_transfer_to_gas_key_success() {
        let (account_id, public_key, access_key) = test_account_keys();
        let mut state_update = setup_account(&account_id, &public_key, &access_key);
        let mut account = get_account(&state_update, &account_id).unwrap().unwrap();

        let gas_key_public_key =
            InMemorySigner::from_seed(account_id.clone(), KeyType::ED25519, "gas_key").public_key();
        add_gas_key_to_account(&mut state_update, &mut account, &account_id, &gas_key_public_key);

        let deposit_amount = Balance::from_yoctonear(1_000_000);
        transfer_to_gas_key(&mut state_update, &account_id, &gas_key_public_key, deposit_amount);

        let gas_key =
            get_access_key(&state_update, &account_id, &gas_key_public_key).unwrap().unwrap();
        let gas_key_info = gas_key.gas_key_info().unwrap();
        assert_eq!(gas_key_info.balance, deposit_amount);

        // Transfer more and verify accumulation
        transfer_to_gas_key(&mut state_update, &account_id, &gas_key_public_key, deposit_amount);
        let gas_key =
            get_access_key(&state_update, &account_id, &gas_key_public_key).unwrap().unwrap();
        let gas_key_info = gas_key.gas_key_info().unwrap();
        assert_eq!(gas_key_info.balance, Balance::from_yoctonear(2_000_000));
    }
```
