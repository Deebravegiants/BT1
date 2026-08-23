This is a real, confirmed analog. The `AddressRegistrar::register` function is deployed as `address-map.near` and is called by the Wallet Contract (an unprivileged, protocol-integrated contract reachable from any Ethereum-style transaction routed through `rlp_execute`) to resolve ETH addresses to NEAR account IDs.

### Title
`AddressRegistrar::register` keeps excess attached deposit instead of refunding it beyond storage cost - (File: `runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs`)

### Summary
`register` requires `given_deposit >= required_deposit` but on the success path (`Entry::Vacant`) it never refunds the difference between `given_deposit` and `required_deposit`; the entire attached deposit is retained by the contract. This mirrors the reported `buyPosition` pattern: a `>=` check is used to validate a payment against a required minimum, but any surplus above that minimum is not returned to the payer.

### Finding Description
In `register` [1](#0-0) , the contract computes `required_deposit` from the storage bytes needed and only checks `given_deposit < required_deposit` to reject calls, using a strict "at least" comparison rather than an exact-match. When the entry is vacant (successful registration), it inserts the mapping and returns without computing or refunding `given_deposit - required_deposit` [2](#0-1) . Only the `Entry::Occupied` (collision) branch refunds the full deposit, because in that case no storage was consumed [3](#0-2) . This is confirmed by the test `test_register_without_deposit`, which asserts the registrar's balance increases by at least the full `deposit_amount` even though `deposit_amount` (320000000000000000000 yoctoNEAR) is chosen without regard to the actual computed storage cost [4](#0-3) . Likewise `test_caller_refunds` explicitly documents "External caller does not get a refund when their tokens are spent" and asserts the debited amount is `>= deposit_amount` (the full amount, not the smaller storage requirement) [5](#0-4) .

This contract is not a demo/mocked artifact: it is deployed under the well-known account id `address-map.near` [6](#0-5)  and is invoked by the protocol's ETH Wallet Contract during `rlp_execute` address-check flows for EOA base-token transfers [7](#0-6) , reachable from any unprivileged Ethereum-style transaction relayed to an ETH-implicit NEAR account.

### Impact Explanation
Any unprivileged caller (directly, or a relayer submitting an Ethereum-signed transaction on behalf of an ETH-implicit account via the Wallet Contract) who attaches more than the exact storage cost when calling `register` permanently loses the surplus into the `address-map.near` contract's balance instead of receiving a refund. This is an unauthorized/unintended balance loss for the caller analogous to "buyer will incur unnecessary loss" in the referenced report — funds are retained by the contract beyond what is economically justified (storage staking), with no path to reclaim them.

### Likelihood Explanation
Likelihood is moderate: the caller (or in practice, a relayer building the underlying Ethereum transaction / NEAR wrapper transaction) chooses the attached deposit amount and has no reliable way to know the exact `storage_byte_cost * bytes_to_store` value at call time (it depends on account id length and current storage price), so over-attaching is a natural/likely occurrence, especially by relayers using a fixed generous deposit constant (as seen in the codebase's own `NEP_141_STORAGE_DEPOSIT_AMOUNT`/registration deposit patterns elsewhere) rather than computing the exact byte cost.

### Recommendation
Compute `deposit_refund = given_deposit.checked_sub(required_deposit)` in the `Entry::Vacant` success branch and issue a `promise_batch_action_transfer` back to `env::predecessor_account_id()` for the surplus, mirroring the exact-cost refund pattern already used for `DeterministicStateInitAction` in the core runtime [8](#0-7) .

### Proof of Concept
1. Deploy/observe `address-map.near` (the `AddressRegistrar` contract).
2. Call `register({"account_id": "alice.near"})` with an attached deposit far exceeding the byte-cost of storing a 20-byte address key plus the account id string (e.g. attach 1 NEAR when the true storage cost is a few hundred microNEAR, as in `test_register_without_deposit` which uses a deposit disconnected from the actual computed `required_deposit`) [9](#0-8) .
3. Observe the registrar's account balance increases by the entire attached deposit, not just `required_deposit`; the caller has no way to retrieve the difference.

### Citations

**File:** runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs (L48-61)
```rust
        // Must store the address and the account id
        let bytes_to_store = 20 + (account_id.len() as u128);
        let required_deposit =
            NearToken::from_yoctonear(env::storage_byte_cost().as_yoctonear() * bytes_to_store);
        let given_deposit = env::attached_deposit();
        // The caller must pay for the storage cost of registering.
        if given_deposit < required_deposit {
            let message = format!(
                "Insufficient deposit to cover storage cost. Given={} Expected={}",
                given_deposit.as_yoctonear(),
                required_deposit.as_yoctonear(),
            );
            env::panic_str(&message);
        }
```

**File:** runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs (L65-72)
```rust
        match self.addresses.entry(address) {
            Entry::Vacant(entry) => {
                let address = format!("0x{}", hex::encode(address));
                let log_message = format!("Added entry {} -> {}", address, account_id);
                entry.insert(account_id);
                env::log_str(&log_message);
                Some(address)
            }
```

**File:** runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs (L73-85)
```rust
            Entry::Occupied(entry) => {
                let log_message = format!(
                    "Address collision between {} and {}. Keeping the former.",
                    entry.get(),
                    account_id
                );
                env::log_str(&log_message);
                // Transfer the deposit back to the caller since no storage was updated.
                let refund_promise = env::promise_batch_create(&env::predecessor_account_id());
                env::promise_batch_action_transfer(refund_promise, given_deposit);
                None
            }
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L215-226)
```rust
    // External caller does not get a refund when their tokens are spent
    let pre_tx_account_balance = post_tx_account_balance;
    let receiver_id = address_registrar.id();
    let result = wallet_contract
        .rlp_execute_from(&caller, receiver_id.as_str(), &create_tx(receiver_id, 1), deposit_amount)
        .await?;
    assert!(result.success);
    let post_tx_account_balance = caller.view_account().await?.balance;
    assert!(
        pre_tx_account_balance.as_yoctonear() - post_tx_account_balance.as_yoctonear()
            >= deposit_amount.as_yoctonear()
    );
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L249-275)
```rust
/// Test asserting the address registrar requires a deposit.
#[tokio::test]
async fn test_register_without_deposit() -> anyhow::Result<()> {
    let TestContext { worker, address_registrar, .. } = TestContext::new().await?;

    let method = "register";
    let args = br#"{"account_id": "birchmd.near"}"#;
    let result = address_registrar.call(method).args(args.to_vec()).transact().await?;
    assert!(result.is_failure(), "Call without deposit must fail");

    let pre_tx_account_balance = address_registrar.as_account().view_account().await?.balance;
    let deposit_amount = NearToken::from_yoctonear(320000000000000000000);
    let result = worker
        .root_account()?
        .call(address_registrar.id(), method)
        .args(args.to_vec())
        .deposit(deposit_amount)
        .transact()
        .await?;

    let output: Option<String> = result.json()?;
    assert_eq!(output.as_deref(), Some("0x4bfcff9a964925adf801c866f6ada98bd7ec40ca"));
    let post_tx_account_balance = address_registrar.as_account().view_account().await?.balance;
    assert!(
        post_tx_account_balance.as_yoctonear() - pre_tx_account_balance.as_yoctonear()
            >= deposit_amount.as_yoctonear()
    );
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/ADDRESS_REGISTRAR_ACCOUNT_ID (L1-1)
```text
address-map.near
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L412-432)
```rust
    let promise = match transaction_kind {
        TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
            address_check: Some(address),
            ..
        }) => {
            let callback_gas = ADDRESS_CHECK_CALLBACK_GAS.saturating_add(action.gas());
            let ext = WalletContract::ext(current_account_id).with_static_gas(callback_gas);
            let address_registrar = {
                let account_id = ADDRESS_REGISTRAR_ACCOUNT_ID
                    .trim()
                    .parse()
                    .unwrap_or_else(|_| env::panic_str("Invalid address registrar"));
                ext_registrar::ext(account_id).with_static_gas(REGISTRAR_LOOKUP_GAS)
            };
            let address = format!("0x{}", hex::encode(address));
            address_registrar.lookup(address).then(ext.address_check_callback(
                target,
                action,
                caller_deposit,
            ))
        }
```

**File:** runtime/runtime/src/deterministic_account_id.rs (L57-91)
```rust
    // Use attached deposit to satisfy storage staking requirements and refund
    // the rest.
    let deposit_refund = match check_storage_stake(account, account.amount(), &apply_state.config) {
        Ok(_) => {
            // no additional storage needed, refunding all
            action.deposit
        }
        Err(StorageStakingError::LackBalanceForStorageStaking(missing_amount)) => {
            if missing_amount <= action.deposit {
                // use exactly as much as needed and refund the rest
                let new_balance = safe_add_balance(account.amount(), missing_amount)?;
                account.set_amount(new_balance);
                action
                    .deposit
                    .checked_sub(missing_amount)
                    .expect("just checked missing_amount <= action.deposit")
            } else {
                result.result = Err(ActionErrorKind::LackBalanceForState {
                    account_id: account_id.clone(),
                    amount: missing_amount,
                }
                .into());
                return Ok(());
            }
        }
        Err(StorageStakingError::StorageError(err)) => {
            return Err(RuntimeError::StorageError(StorageError::StorageInconsistentState(err)));
        }
    };

    if deposit_refund > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(receipt.balance_refund_receiver(), deposit_refund));
    }
```
