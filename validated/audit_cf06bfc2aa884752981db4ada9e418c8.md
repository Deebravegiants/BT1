### Title
`DeleteAccount` silently burns gas-key balances instead of transferring them to the beneficiary, contradicting documented behavior - (File: runtime/runtime/src/actions.rs)

### Summary
The external report describes `PartyGovernanceNFT.rageQuit()`: a withdrawal function that is documented/expected to pay a user their fair share of all treasury asset types, but silently fails to move one specific asset class (ERC1155), causing that value to be lost/stuck instead of transferred. The nearcore analog is `action_delete_account`: the `DeleteAccount` action is documented as transferring "the remaining account balance" to `beneficiary_id`, but gas-key balances held by the deleted account are not transferred — they are destroyed (added to `tokens_burnt`) instead.

### Finding Description
`action_delete_account` computes the account's liquid balance and pushes a `Receipt::new_balance_refund` to send it to `beneficiary_id`: [1](#0-0) 

But before that, it separately sums up all gas-key balances on the account via `compute_gas_key_balance_sum`, and if that sum is within the burn threshold, it adds the amount to `result.tokens_burnt` (i.e. destroys it) rather than including it in the balance transferred to the beneficiary: [2](#0-1) 

This mirrors `delete_gas_key`, which explicitly burns a single gas key's balance on `DeleteKey` rather than crediting the account: [3](#0-2) 

The documentation for `DeleteAccountAction` states only that "the account, as well as all the data stored under the account, is deleted and the tokens are transferred to `beneficiary_id`" — it makes no mention of gas-key balances being excluded/burned instead of transferred: [4](#0-3) 

This is the same shape of bug as the ERC1155 rageQuit report: a fund-recovery/close-out action is documented to move "the remaining value" to a recipient, but one specific balance component (gas-key balance, analogous to the ERC1155 token type) is not moved through that path and is instead destroyed, causing a loss of value relative to the documented/expected behavior. Unlike the withdraw-from-gas-key path (`action_withdraw_from_gas_key`), which correctly credits the account amount, `action_delete_account` bypasses that path entirely for gas-key funds.

### Impact Explanation
Any account holder with funded gas keys who deletes their account (a fully unprivileged, self-service transaction) loses up to `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR) worth of tokens that are burned rather than transferred to the chosen beneficiary. This is a genuine, protocol-level value-destruction bug reachable by any signer via a normal `DeleteAccount` transaction — it does not require validator or node privileges. While bounded to 1 NEAR per account (accounts with gas-key balances exceeding that threshold are blocked from deletion with `GasKeyBalanceTooHigh`), it is a concrete, silent loss of user funds inconsistent with the documented "tokens transferred to beneficiary" behavior, directly analogous to the "undocumented value leakage" the C4 judge cited as meeting medium severity in the original report.

### Likelihood Explanation
High likelihood of occurrence in practice: any user who funds a gas key (via `TransferToGasKey`) and later deletes the parent account without first calling `WithdrawFromGasKey` to move the balance out will trigger this burn automatically and silently — there is no warning, error, or partial-success signal distinguishing "balance transferred" from "balance burned." Because gas keys are a newly introduced primitive (protocol feature `GasKeys`), users and integrators are likely unaware that `DeleteAccount` does not sweep gas-key balances to the beneficiary, unlike the main account balance.

### Recommendation
Modify `action_delete_account` so gas-key balances are added to the beneficiary transfer (`account_balance` used to build the `Receipt::new_balance_refund`) rather than to `result.tokens_burnt`, mirroring how `action_withdraw_from_gas_key` moves gas-key funds into the account balance. If burning is intentional (e.g., to avoid re-processing many nonce records), this must be explicitly documented in `docs/RuntimeSpec/Actions.md` and surfaced via a distinct, unambiguous outcome/log so users are not surprised by silent fund loss, matching the recommendation from the original report to make asset-class handling in a withdrawal/close-out action complete and documented.

### Proof of Concept
1. Create account `A` with an access key.
2. `A` calls `AddKey` with a `GasKeyInfo` permission to add a gas key `K`, then `TransferToGasKey` to fund `K` with, e.g., 500 milliNEAR (`test_delete_account_burns_gas_key_balances` demonstrates the mechanics): [5](#0-4) 
3. `A` submits `DeleteAccount { beneficiary_id: B }` without first withdrawing the gas-key funds.
4. `action_delete_account` computes `gas_key_balance_to_burn` from all of `A`'s gas keys, and — because it is below `MAX_BALANCE_TO_BURN` — adds it to `result.tokens_burnt` instead of to the beneficiary's transfer receipt: [6](#0-5) 
5. Result: `B` only receives `account.amount()` (the regular liquid balance); the gas-key balance is permanently destroyed, even though the action's documentation and its `beneficiary_id` field imply the full remaining value of the account is transferred.

### Citations

**File:** runtime/runtime/src/actions.rs (L354-376)
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
    // We use current amount as a pay out to beneficiary.
    let account_balance = account_ref.amount();
    if account_balance > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance));
    }
    let remove_result = remove_account(state_update, account_id)?;
    result.tokens_burnt =
        result.tokens_burnt.checked_add(gas_key_balance_to_burn).ok_or_else(|| {
            StorageError::StorageInconsistentState("tokens_burnt overflow".to_string())
        })?;
    if remove_result.gas_key_nonce_count > 0 {
```

**File:** runtime/runtime/src/access_keys.rs (L103-113)
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
    result.tokens_burnt =
        result.tokens_burnt.checked_add(gas_key_info.balance).ok_or(IntegerOverflowError)?;
```

**File:** runtime/runtime/src/access_keys.rs (L716-751)
```rust
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
```

**File:** docs/RuntimeSpec/Actions.md (L278-289)
```markdown
## DeleteAccountAction

```rust
pub struct DeleteAccountAction {
    /// The remaining account balance will be transferred to the AccountId below
    pub beneficiary_id: AccountId,
}
```

**Outcomes**:

- The account, as well as all the data stored under the account, is deleted and the tokens are transferred to `beneficiary_id`.
```
