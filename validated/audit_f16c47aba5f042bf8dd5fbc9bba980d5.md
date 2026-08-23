### Title
Excess attached deposit not refunded on successful registration in `AddressRegistrar::register()` - (File: `runtime/near-wallet-contract/implementation/address-registrar/src/lib.rs`)

### Summary
`AddressRegistrar::register()` is a `#[payable]` method that requires the caller to attach enough deposit to cover the storage cost of the new `address -> account_id` entry. It correctly rejects calls where the attached deposit is *insufficient*, and it correctly refunds the *entire* deposit when the call fails due to an address collision. However, when registration succeeds and the caller attaches **more** than the required storage deposit, the excess amount is never refunded — the whole `given_deposit` is silently kept by the contract with no mechanism to reclaim it.

### Finding Description
In the success path (`Entry::Vacant`), the code only checks `given_deposit < required_deposit` and panics if insufficient: [1](#0-0) 

But once the check passes and the entry is inserted, there is no logic that computes `given_deposit - required_deposit` and returns it to the caller: [2](#0-1) 

Contrast this with the collision branch, which explicitly issues a `Transfer` promise back to `env::predecessor_account_id()` for the *full* deposit when the registration fails, proving that the developer is aware refunding is the intended pattern for unused deposit, but simply omitted it for the "overpayment" case: [3](#0-2) 

There is no other method (e.g., a withdraw/sweep function) in the contract that would let a user or owner later reclaim the stranded excess balance, so the tokens are permanently retained by the contract account.

This is the direct analog of the reported Solidity bug: `mintFee`-style logic in `MysteryBox::revealMysteryBoxes()` checks `msg.value >= mintFee` but does not refund `msg.value - mintFee`, causing user loss. `AddressRegistrar::register()` checks `given_deposit >= required_deposit` but does not refund `given_deposit - required_deposit`, causing the same class of unrefunded-overpayment loss.

### Impact Explanation
Any unprivileged account can call `register(account_id)` as part of a standard `FunctionCall` action with an attached deposit. If the caller (often a wallet or tooling that estimates storage cost imprecisely and adds a safety margin) attaches more than the exact required storage deposit, the excess is transferred into the contract's balance and is unrecoverable by the user. This is a real balance loss reachable from an ordinary, unprivileged transaction — not a validator/mocked/dependency-only path — and the address-registrar contract is a production component of the `near-wallet-contract` implementation (NEP-518 wallet contract tooling) shipped in this repository.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: callers must estimate the exact storage cost (`storage_byte_cost * bytes_to_store`) to avoid overpaying, and any small overestimate (a common defensive practice against fluctuating storage prices or `account_id` length miscalculation) results in permanent fund loss with no error, warning, or recovery path.

### Recommendation
In the `Entry::Vacant` success branch, compute `let excess = given_deposit.checked_sub(required_deposit)` and, if greater than zero, issue a `promise_batch_action_transfer` back to `env::predecessor_account_id()` for the excess amount, mirroring the refund already performed in the `Entry::Occupied` branch. Alternatively, require an exact deposit match (`given_deposit != required_deposit` should panic) if partial refunds are undesirable.

### Proof of Concept
1. Compute `required_deposit` for a target `account_id` (`storage_byte_cost * (20 + account_id.len())`).
2. Submit a `FunctionCall` transaction calling `register(account_id)` on the `AddressRegistrar` contract with `attached_deposit = required_deposit + X` (X > 0), from an unprivileged account.
3. Observe: the call succeeds (address is registered), the contract's account balance increases by `required_deposit + X`, and no refund receipt is generated back to the caller — reference the refund logic that *is* present only in the collision branch: [4](#0-3) . The `X` excess is permanently unrecoverable by the caller.

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
