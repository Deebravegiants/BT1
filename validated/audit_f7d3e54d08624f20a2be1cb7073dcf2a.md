### Title
NFT transfer does not restamp `Account.owner`, leaving the prior owner (and their delegates) authorized to withdraw and borrow against the transferred account - (File: contracts/controller/src/account.rs)

### Summary
CVE-2016-1905's class is "the access check consults the wrong/stale object, so an authenticated caller reaches resources it should not." The controller's account record caches `owner` at mint time (`create_account`), while the authoritative ownership is the transferable position NFT, read separately via `storage::account_owner` in `require_account_owner`. The sensitive value-moving paths — `process_borrow` and `process_withdraw` — gate on `require_owner_or_delegate(..., &account.owner)`, i.e. the *stored* owner, not the current NFT owner. After a transfer, the previous holder still satisfies `caller == owner` in `is_owner_or_delegate` and retains full control of the account's collateral and borrowing power.

### Finding Description
- `create_account` stores `Account { owner: owner.clone(), .. }` at mint time (`account.rs:64-70`). `load_or_create_account` / `storage::get_account` return this stored `owner` — nothing in the account-loading path shown restamps it from the NFT contract.
- `require_account_owner` (used by `renew_account`, `add_delegate`, `remove_delegate`) explicitly re-reads the NFT owner via `storage::account_owner(env, account_id)` and compares to `caller` (`account.rs:143-148`). The existence of a separate, NFT-based ownership check alongside the stored `Account.owner` indicates the two can diverge — otherwise one would suffice.
- `process_borrow` (`positions/debt.rs:40-45`) and `process_withdraw` (`positions/supply.rs:147-154`) only require `require_owner_or_delegate(env, account_id, caller, &account.owner)`, where `is_owner_or_delegate` returns true when `caller == owner` (`account.rs:121-122`). Both accept a `to: Option<Address>` recipient and only require it to be an external recipient.
- Delegate authority is keyed on the stored owner too: `is_owner_or_delegate` checks `storage::get_delegates(env, account_id, owner)` (`account.rs:126`), and `set_account_delegate` writes delegates under the *current NFT owner* `caller` (`account.rs:260-264`). So a new owner's `add_delegate` grants are keyed under the new owner and are never consulted, while the *old* owner's delegate list remains effective under `account.owner`.

### Impact Explanation
Theft of user funds: after an account NFT is sold or transferred, the original owner can still call `withdraw(account_id, withdrawals, Some(self))` to drain all supplied collateral, and `borrow(account_id, borrows, Some(self))` to take loans against the victim's collateral to any external recipient — leaving the new NFT holder with an empty or insolvent position. This is a direct analog of the advisory: authenticated principals retain access to resources after the object's ownership has changed.

### Likelihood Explanation
Requires the victim to acquire a position NFT that already has collateral — an intended usage (NFT is `transfer`/`approve`-able per scope). The attacker path is a single unprivileged transaction by the previous owner; no privileged role, oracle manipulation, or cross-contract assumption is needed. Severity rests on whether `storage::get_account` re-syncs `owner` from the NFT; if it does not (and `require_account_owner` strongly suggests it does not), the exploit is deterministic.

### Recommendation
Make `require_owner_or_delegate` consult `storage::account_owner(env, account_id)` (NFT `owner_of`) instead of `Account.owner`, or refresh `account.owner` from the NFT on every `get_account`/load. Also re-key the delegate map on NFT ownership transitions, or key delegates by `account_id` alone and re-validate the grantor is the current owner at delegation time.

### Proof of Concept
1. Alice calls `supply(spoke_id, assets)` → mints `account_id` with `Account.owner = Alice` and NFT owner Alice.
2. Alice transfers the position NFT to Bob via the position-nft `transfer` entrypoint (or sells it on a marketplace).
3. Bob adds collateral: `supply(account_id, more)` — succeeds since `require_third_party_existing_supply`/owner checks pass for the NFT holder's deposits.
4. Alice calls `withdraw(account_id, withdrawals, to = Some(Alice))`. `require_owner_or_delegate` passes because `account.owner` still equals Alice. The pool pays out Bob's collateral to Alice.
5. Optionally Alice calls `borrow(account_id, borrows, to = Some(Alice))` up to the HF limit, strapping debt to Bob's account.

Caveat: this finding depends on `Account.owner` remaining stale after an NFT transfer — I could not fully verify whether `storage::get_account` or the position-nft transfer hook resynchronizes `owner`, due to limited inspection of `storage/account.rs` and the NFT transfer path. If a transfer callback restamps `Account.owner`, this analog is invalid and no vulnerability is present. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/controller/src/account.rs (L62-74)
```rust
    let nft = storage::get_position_nft(env);
    let account_id = nft_mint_call(env, &nft, owner);
    let account = Account {
        owner: owner.clone(),
        spoke_id,
        mode,
        supply_positions: Map::new(env),
        borrow_positions: Map::new(env),
    };
    storage::set_account_meta(env, account_id, &AccountMeta { spoke_id, mode });

    (account_id, account)
}
```

**File:** contracts/controller/src/account.rs (L115-148)
```rust
pub(crate) fn is_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) -> bool {
    if caller == owner {
        return true;
    }
    let active_manager =
        storage::get_position_manager(env, caller).is_some_and(|config| config.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}

/// Requires the owner or a registered, active manager delegated by that owner.
pub(crate) fn require_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) {
    if is_owner_or_delegate(env, account_id, caller, owner) {
        return;
    }
    panic_with_error!(env, GenericError::NotAuthorized);
}

/// Returns metadata after verifying that `caller` currently owns the account NFT.
pub(crate) fn require_account_owner(env: &Env, account_id: u64, caller: &Address) -> AccountMeta {
    let meta = storage::get_account_meta(env, account_id);
    let owner = storage::account_owner(env, account_id);
    assert_with_error!(env, owner == *caller, GenericError::AccountNotInMarket);
    meta
}
```

**File:** contracts/controller/src/account.rs (L249-264)
```rust
    caller.require_auth();
    require_account_owner(env, account_id, caller);
    if add {
        // Reject dormant grants that could gain authority on later manager activation.
        assert_with_error!(
            env,
            storage::get_position_manager(env, delegate).is_some_and(|c| c.is_active),
            GenericError::NotAuthorized
        );
    }

    let changed = if add {
        storage::add_delegate(env, account_id, caller, delegate)
    } else {
        storage::remove_delegate(env, account_id, caller, delegate)
    };
```

**File:** contracts/controller/src/positions/debt.rs (L40-47)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
```

**File:** contracts/controller/src/positions/supply.rs (L147-155)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);
```
