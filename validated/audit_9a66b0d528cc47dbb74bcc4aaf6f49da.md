### Title
Stale `Account.owner` grants the previous NFT holder owner-level authority after a position transfer - (File: contracts/controller/src/account.rs)

### Summary
The CVE's bug class is "policy matched against mutable, non-canonical identity metadata" (Matrix `allowFrom` matching display names instead of MXIDs). The lending analog lives in the controller's dual notion of account ownership: the `Account` struct stores `owner` once at account creation, while `require_account_owner` authorizes against the *live* NFT `owner_of` via `storage::account_owner`. Since the position NFT is freely transferable and transfer never updates `Account.owner`, paths that check `caller == account.owner` (`is_owner_or_delegate` / `require_owner_or_delegate`) keep recognizing the *previous* holder — the analog of matching a stale/mutable name instead of the canonical identity.

### Finding Description
- `create_account_with` writes `Account { owner: owner.clone(), ... }` at mint time; nothing ever rewrites `account.owner` [1](#0-0) .
- The position NFT is a standard transferable OZ enumerable token; `transfer`/`approve` come from `stellar_tokens` and there is no controller hook or callback that syncs `Account.owner` on transfer — the NFT only exposes `mint`, `burn`, `renew`, `upgrade` to the controller [2](#0-1) .
- `is_owner_or_delegate` returns `true` when `caller == owner`, where `owner` is the stale `account.owner` field, not the NFT owner [3](#0-2) .
- `require_owner_or_delegate` is used by `AccountGuard::Migrate` and `AccountGuard::Multiply` in `load_or_create_account`, so a prior holder who sold/transferred the position NFT still passes the owner check on those flows [4](#0-3) .
- The same staleness poisons delegation: `get_delegates(env, account_id, owner)` is keyed by the stale `account.owner`, so delegates registered by the seller remain authorized, and the new NFT owner cannot revoke them — `remove_delegate` calls `storage::remove_delegate(env, account_id, caller, delegate)` under the *new* owner's key while the grant lives under the old one [5](#0-4) [6](#0-5) .
- Note the asymmetry proving this is unintended: owner-only maintenance paths (`renew_account`, `add_delegate`, `remove_delegate`) deliberately check the canonical NFT owner via `require_account_owner`, while action paths (Migrate/Multiply guards) check the stale field [7](#0-6) .

### Impact Explanation
An unprivileged address can (a) acquire a position legitimately, (b) register an active manager as delegate, (c) transfer/sell the NFT, and (d) retain owner-or-delegate authority over the account forever. Through `migrate_from_blend` / `multiply` (the `Migrate`/`Multiply` guards) the stale owner or their delegate can re-enter the account and take actions — including multiplying debt against collateral now owned by the buyer — degrading the new owner's health factor or extracting borrowed value. Theft of user funds / theft of collateral value. Severity: High.

### Likelihood Explanation
Position NFT transfers are explicitly in the allowed attack surface (`position-nft transfer/approve`), and every step is a permissionless entrypoint call by a single address. The only precondition for the delegate variant is the existence of an `is_active` position manager, which is a normal protocol feature; the direct `caller == owner` variant requires nothing at all. I did not fully verify whether downstream `multiply`/`migrate` disburse proceeds to `caller` vs. `account.owner` — if proceeds go to the stale `account.owner`, impact is direct theft; if they stay in-account, impact is forced leverage/liquidation risk on the victim. Either way the unauthorized-control primitive is proven by the code above.

### Recommendation
Treat NFT `owner_of` as the single source of truth: in `is_owner_or_delegate`, replace the `caller == owner` shortcut and the delegate-map key with `storage::account_owner(env, account_id)` (or drop `Account.owner` entirely). Alternatively, make the NFT non-transferable or add a controller-mediated transfer that rewrites `Account.owner` and migrates/clears the delegate set.

### Proof of Concept
1. Alice calls `supply` with `account_id = 0` → `create_account` mints NFT `id = N`, stores `Account.owner = Alice`.
2. Alice calls `add_delegate(N, M)` where `M` is an active position manager (optional amplification).
3. Alice calls `PositionNft::transfer(Alice, Bob, N)`.
4. Alice (or `M`) calls `multiply(account_id = N, ...)` / `migrate_from_blend`: `load_or_create_account` → `require_owner_or_delegate` → `is_owner_or_delegate` sees `caller == account.owner == Alice` → authorized, despite `owner_of(N) == Bob`. Bob cannot revoke `M` because `remove_delegate` looks up delegates under Bob's key while the grant was stored under Alice's.

### Citations

**File:** contracts/controller/src/account.rs (L62-71)
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
```

**File:** contracts/controller/src/account.rs (L98-110)
```rust
    let account = storage::get_account(env, account_id);
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
        }
    }
```

**File:** contracts/controller/src/account.rs (L115-127)
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
```

**File:** contracts/controller/src/account.rs (L143-148)
```rust
pub(crate) fn require_account_owner(env: &Env, account_id: u64, caller: &Address) -> AccountMeta {
    let meta = storage::get_account_meta(env, account_id);
    let owner = storage::account_owner(env, account_id);
    assert_with_error!(env, owner == *caller, GenericError::AccountNotInMarket);
    meta
}
```

**File:** contracts/controller/src/account.rs (L242-275)
```rust
fn set_account_delegate(
    env: &Env,
    caller: &Address,
    account_id: u64,
    delegate: &Address,
    add: bool,
) {
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

    if changed {
        AccountDelegateEvent {
            account_id,
            owner: caller.clone(),
            delegate: delegate.clone(),
            granted: add,
        }
        .publish(env);
    }
}
```

**File:** contracts/position-nft/src/contract.rs (L2-5)
```rust
//! the account id. The token owner (`owner_of`) is the account owner.
//! Mint, burn and upgrade are controller-only; `renew` is permissionless. The
//! rest is the stock OpenZeppelin non-fungible interface with a custom
//! `token_uri`.
```
