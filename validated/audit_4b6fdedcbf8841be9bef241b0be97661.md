### Title
Excess Attached Deposit Permanently Locked in `AddressRegistrar::register` - (File: `runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs`)

### Summary
The `register()` method of the `AddressRegistrar` contract only validates that the attached deposit is *at least* the required storage cost (`given_deposit < required_deposit`), but never refunds the difference on the success path. Any excess NEAR sent above the storage cost is silently absorbed into the contract's balance with no accounting or recovery mechanism, mirroring the `depositNative()` overpayment-lock bug described in the external report.

### Finding Description
`register()` is a `#[payable]` public method that computes `required_deposit` from the number of bytes needed to store the `address -> account_id` mapping, then reads `given_deposit = env::attached_deposit()`. It only guards against under-payment: [1](#0-0) 

There is no `given_deposit == required_deposit` check and no refund of `given_deposit - required_deposit`. On the success path (`Entry::Vacant`), the full `given_deposit` is retained by the contract even though only `required_deposit` yoctoNEAR is actually needed to cover the storage staking cost: [2](#0-1) 

Notably, the contract authors were clearly aware that excess deposits need to be returned — but only implemented the refund for the collision/failure branch (`Entry::Occupied`), where the *entire* `given_deposit` is sent back because no storage was written: [3](#0-2) 

This is the exact analog of the reported `depositNative()` bug: the contract accepts `msg.value`/`attached_deposit` greater than the amount it actually needs (`_amount`/`required_deposit`), performs the intended action using only the needed portion, and never refunds the surplus on the success path, even though a refund code path already exists elsewhere in the same function for a different scenario.

### Impact Explanation
Any caller who attaches more NEAR than the exact storage cost required for their `account_id` length permanently loses the difference — it becomes stranded balance owned by the `AddressRegistrar` contract account with no withdrawal method exposed anywhere in the contract's public interface (`register`, `lookup`, `get_address`). Because callers must compute `required_deposit` precisely off-chain (`storage_byte_cost() * (20 + account_id.len())`), any rounding, estimation buffer, or reused prior deposit values (a common client pattern of over-attaching to avoid `Insufficient deposit` panics) results in unrecoverable fund loss. Given the wallet-contract/address-registrar is meant to support the broader eth-implicit account registration flow, this could affect users interacting with that flow at scale.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: `required_deposit` depends on `account_id` length and the current `storage_byte_cost`, both of which callers must reproduce exactly off-chain to avoid overpaying; any client that pads the deposit for safety (a common defensive pattern, since underpaying causes an outright panic) will trigger permanent fund loss on every successful call.

### Recommendation
Change the success (`Entry::Vacant`) branch to refund `given_deposit - required_deposit` back to `env::predecessor_account_id()`, mirroring the refund logic already used in the `Entry::Occupied` branch, or enforce strict equality (`given_deposit != required_deposit` → panic) as recommended in the referenced report for `depositNative()`.

### Proof of Concept
1. Compute `account_id_to_address` for a target `account_id` and derive `required_deposit = storage_byte_cost() * (20 + account_id.len())`.
2. Call `register(account_id)` with `attached_deposit = required_deposit + X` (X > 0), where the address is not yet registered.
3. Execution takes the `Entry::Vacant` branch: the mapping is inserted successfully and `Some(address)` is returned, but no refund receipt is created for the excess `X`.
4. The `AddressRegistrar` contract's on-chain balance permanently increases by `X` with no method available to the original caller (or anyone) to reclaim it.

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
