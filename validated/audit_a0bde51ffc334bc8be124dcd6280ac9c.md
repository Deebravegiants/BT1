### Title
External Attacker Can Permanently Lock Account by Overfunding a `GasKeyFunctionCall` Key - (File: `runtime/runtime/src/access_keys.rs`)

---

### Summary

An external attacker can permanently lock a victim's NEAR account by sending a `TransferToGasKey` action that pushes the victim's `GasKeyFunctionCall` key balance above `GasKeyInfo::MAX_BALANCE_TO_BURN` (1 NEAR). If the victim's only signing key is a `GasKeyFunctionCall` key, they cannot sign a `WithdrawFromGasKey` transaction to reduce the balance, and cannot delete the key or the account. The account enters a permanently unrecoverable locked state with no protocol-level escape path.

---

### Finding Description

**Root cause — deletion guard in `delete_gas_key`:**

In `runtime/runtime/src/access_keys.rs`, `delete_gas_key` unconditionally blocks deletion when the gas key balance exceeds `MAX_BALANCE_TO_BURN`:

```rust
if gas_key_info.balance > GasKeyInfo::MAX_BALANCE_TO_BURN {
    result.result = Err(ActionErrorKind::GasKeyBalanceTooHigh { ... }.into());
    return Ok(());
}
```

`MAX_BALANCE_TO_BURN` is defined as exactly 1 NEAR:

```rust
pub const MAX_BALANCE_TO_BURN: Balance = Balance::from_near(1);
```

The same guard applies to `action_delete_account` in `runtime/runtime/src/actions.rs`, which checks the aggregate gas key balance sum before allowing account deletion.

**Attacker-controlled entry path — `TransferToGasKey` has no sender restriction:**

The `TransferToGasKey` action is validated only for protocol version in `validate_action_with_mode`:

```rust
Action::TransferToGasKey(_) => {
    validate_transfer_to_gas_key_action(current_protocol_version)
}
```

There is no check that the transaction sender is the account owner. A transaction with `signer_id = attacker.near` and `receiver_id = victim.near` containing `TransferToGasKey { public_key: victim_gas_key_pk, deposit: 2_NEAR }` is accepted by the runtime and funds the victim's gas key on the victim's account.

**No recovery path for `GasKeyFunctionCall`-only accounts:**

`GasKeyFunctionCall` keys carry `FunctionCallPermission`, restricting them to signing transactions with a single `FunctionCall` action to a specific receiver. A `WithdrawFromGasKey` action is not a `FunctionCall` action, so a `GasKeyFunctionCall` key cannot sign a `WithdrawFromGasKey` transaction.

Additionally, `WithdrawFromGasKey` is explicitly unavailable via contract execution — there is no corresponding promise batch host function:

```rust
/// This action must only be available via transactions, not via contract execution
/// (there is no corresponding promise batch action host function).
pub struct WithdrawFromGasKeyAction { ... }
```

Therefore, if the victim's only signing key is a `GasKeyFunctionCall` key, they cannot:
1. Sign a `WithdrawFromGasKey` transaction (key type restriction)
2. Delete the gas key (balance above threshold)
3. Delete the account (aggregate balance above threshold)
4. Add a new full-access key (key type restriction)
5. Call `WithdrawFromGasKey` from a contract (no host function exists)

---

### Impact Explanation

The corrupted protocol state is the `GasKeyInfo.balance` field stored in the account's trie entry, permanently set above the deletion threshold by the attacker. The concrete consequences are:

- The victim's gas key entry in the trie is permanently undeletable.
- The victim's account is permanently undeletable.
- The victim's account balance (NEAR tokens) is permanently trapped — it cannot be transferred out via `DeleteAccount` (blocked) and cannot be recovered by any other protocol mechanism.
- The victim retains only the ability to make function calls permitted by their `GasKeyFunctionCall` key, but cannot perform any account management operations.

The corrupted DB entry is the `AccessKey` trie value for the victim's gas key, with `GasKeyInfo.balance > 1 NEAR`.

---

### Likelihood Explanation

The precondition is that the victim's account has only a `GasKeyFunctionCall` key and no regular `FullAccess` or `GasKeyFullAccess` key. This is a valid and intended use case: accounts designed for limited, automated, or delegated operation (e.g., smart contract interaction accounts, relayer accounts, or accounts managed by a dApp) may deliberately hold only a function-call-scoped gas key. The `GasKeyFunctionCall` permission type is a new feature in this codebase, and users may not be aware of the permanent-lock risk.

The attacker cost is slightly above 1 NEAR (a one-time expenditure), which is affordable. The attack requires no privileged access, no validator role, and no special network position — only a funded account and knowledge of the victim's gas key public key (which is public on-chain).

---

### Recommendation

1. **Restrict `TransferToGasKey` to self-receipts only**: Require that the `TransferToGasKey` action can only appear in a receipt where the predecessor is the account itself (i.e., only the account owner can fund their own gas key). This eliminates the external funding vector entirely.

2. **Or: Add a host function for `WithdrawFromGasKey`**: Expose `WithdrawFromGasKey` as a promise batch action host function so that a contract can withdraw from a gas key on behalf of the account, providing a recovery path even for `GasKeyFunctionCall`-only accounts.

3. **Or: Cap the gas key balance at deposit time**: In `action_transfer_to_gas_key`, reject deposits that would push the gas key balance above `MAX_BALANCE_TO_BURN`, preventing the balance from ever reaching the undeletable threshold.

---

### Proof of Concept

**Setup:**
- Victim creates account `victim.near` with only a `GasKeyFunctionCall` key (`gas_key_pk`) restricted to calling `method1` on `contract.near`. Gas key balance = 0 NEAR.

**Attack:**
1. Attacker submits a signed transaction:
   - `signer_id`: `attacker.near`
   - `receiver_id`: `victim.near`
   - `actions`: `[TransferToGasKey { public_key: gas_key_pk, deposit: 2_NEAR }]`
2. The runtime applies the action to `victim.near`'s gas key. Gas key balance becomes 2 NEAR.

**Result — permanent lock:**
3. Victim attempts `DeleteKey { public_key: gas_key_pk }`: fails with `GasKeyBalanceTooHigh { balance: 2 NEAR }` at `delete_gas_key` line 103–110.
4. Victim attempts `DeleteAccount { beneficiary_id: ... }`: fails with `GasKeyBalanceTooHigh` at `action_delete_account` line 340–347.
5. Victim attempts to sign `WithdrawFromGasKey { public_key: gas_key_pk, amount: 2_NEAR }`: rejected at transaction validation — the `GasKeyFunctionCall` key cannot authorize a non-`FunctionCall` action.
6. No contract call can invoke `WithdrawFromGasKey` (no host function exists).
7. Victim's account balance is permanently trapped. The `GasKeyInfo.balance` trie entry remains above the deletion threshold with no protocol-level recovery path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** core/primitives-core/src/account.rs (L551-554)
```rust
impl GasKeyInfo {
    /// Maximum gas key balance that can be burned during key or account deletion.
    /// Deletion fails if the (sum of) gas key balance(s) exceeds this threshold.
    pub const MAX_BALANCE_TO_BURN: Balance = Balance::from_near(1);
```

**File:** runtime/runtime/src/actions.rs (L339-347)
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
```

**File:** runtime/runtime/src/action_validation.rs (L171-173)
```rust
        Action::TransferToGasKey(_) => {
            validate_transfer_to_gas_key_action(current_protocol_version)
        }
```

**File:** core/primitives/src/action/mod.rs (L311-332)
```rust
/// Withdraw NEAR from a gas key's balance to the account.
///
/// This action must only be available via transactions, not via contract execution
/// (there is no corresponding promise batch action host function).
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
pub struct WithdrawFromGasKeyAction {
    /// The public key of the gas key to withdraw from
    pub public_key: PublicKey,
    /// Amount of NEAR to transfer from the gas key
    pub amount: Balance,
}
```
