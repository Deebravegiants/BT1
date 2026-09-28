### Title
Archived/evicted position-map entries are silently read as empty, letting an account with live debt or collateral be treated as position-free — ([File: contracts/controller/src/storage/account.rs](contracts/controller/src/storage/account.rs))

### Summary
The USB-disconnect bug class — a resource handle going absent after teardown while callers keep using it — maps onto Soroban persistent-storage archival in the controller. `AccountMeta`, `SupplyPositions`, `BorrowPositions`, and `Delegates` are four independent persistent ledger entries per account, each with its own TTL. Account loading treats a missing `AccountMeta` as fatal (`AccountNotFound`/`AccountNotInMarket`), but treats missing `SupplyPositions`/`BorrowPositions` as an empty map instead of an error — the exact "check for NULL only on some entry points" shape of the kernel bug. [1](#0-0) [2](#0-1) 

### Finding Description
`get_supply_positions` and `get_debt_positions` return `Map::new(env)` when the persistent entry is absent, with no distinction between "account never had this side" and "entry archived/evicted." [3](#0-2)  The asymmetry is compounded by TTL handling: metadata and delegate writes renew user TTL via `set_user`, but `write_side_map` performs a bare `persistent.set`/`remove` with no renewal, so the position maps' TTLs drift independently of the meta entry they depend on. [4](#0-3)  `renew_user_account` only renews keys that currently exist (`persistent.has(key)`), so once a position map expires it is never renewed again even by an honest owner calling `renew_account`. [5](#0-4) 

The disconnect consequence lands in `cleanup_account_if_empty`: when both in-memory maps are empty, the account meta is deleted and the NFT burned via `remove_account_and_burn_nft`. [6](#0-5)  Combined with the default-empty reads, an account whose `SupplyPositions` and `BorrowPositions` entries have archived while `AccountMeta` survives is indistinguishable from a genuinely empty account on any path that loads the account and runs cleanup — e.g., a dust `repay`, a zero-delta `update_indexes`/threshold refresh path that calls cleanup, or liquidation of a "remaining" position. The pool's global books still record the scaled debt/supply shares; the controller's per-account ledger is destroyed, permanently orphaning the obligation.

### Impact Explanation
- **Permanent freezing of funds / insolvency**: once `remove_account_and_burn_nft` fires on an account whose position entries were archived, the NFT is burned and meta deleted; there is no path to re-associate the pool-side scaled balances with an owner. Suppliers' claims backing that debt become unrecoverable — protocol insolvency in the bad-debt sense.
- **Theft via invisible debt**: before cleanup, `get_account` returns an account with `borrow_positions` empty while pool-side debt shares still exist, so health-factor gating sees a debt-free account; any collateral-side path that relies on the loaded account undervalues obligations.
- The trigger needs no privilege: an attacker can open an account, let the position-map TTLs lapse (position-map writes never renew, and `renew_user_account` cannot resurrect an expired key), then submit `repay`/`liquidate`/`update_account_threshold`-family calls that route through `get_account` + `cleanup_account_if_empty`.

### Likelihood Explanation
Medium. TTL expiry is a normal Soroban condition, not an attacker-controlled state, but the code makes it reachable: writes deliberately skip renewal for position maps, reads deliberately default-absent to empty rather than failing closed (contrast `get_account_meta`, which panics `AccountNotInMarket`), and cleanup treats "empty maps" as proof of emptiness despite the load path's own doc admitting "the empty supply map does not prove supply is absent." [7](#0-6)  Any keeper gap or inactive-account drift creates the precondition without attacker cost beyond opening an account.

### Recommendation
Mirror the kernel fix — validate the "interface" at every entry point rather than defaulting:
1. In `try_get_account`/`get_account`, treat a *surviving* `AccountMeta` with missing position entries as a distinct state: fail with a restorable error (e.g., `AccountStateUnavailable`) instead of returning empty maps, or at minimum skip `cleanup_account_if_empty` when either `persistent.has()` check shows the key never existed vs. was archived.
2. Have `write_side_map` renew the key it writes, keeping position-map TTLs coupled to account activity.
3. Gate `cleanup_account_if_empty` on `persistent.has(SupplyPositions/BorrowPositions)` returning `false` by confirmed deletion, not by load default.

### Proof of Concept
1. Unprivileged user calls `supply` (creates account `A` with `AccountMeta` + `SupplyPositions(A)`), then `borrow` (writes `BorrowPositions(A)` — no TTL renew on the write).
2. User lets `SupplyPositions(A)`/`BorrowPositions(A)` entries expire (persistent TTL lapse), while `AccountMeta(A)` remains live (it was renewed by meta/delegate writes or `renew_account`).
3. Any call that loads the account — e.g., `repay(account_id=A, ...)` with a token the account "has no" debt in, or liquidation/`update_account_threshold` flowing into cleanup — executes `get_account`, which returns `Some(Account)` with empty maps instead of failing.
4. `cleanup_account_if_empty` observes `account.is_empty()`, calls `remove_account_and_burn_nft`: meta, maps, and delegates deleted; NFT burned.
5. The pool still holds the scaled debt/supply for `A`'s hub assets, but no owner or account exists to repay or claim — the obligation is permanently orphaned.

### Citations

**File:** contracts/controller/src/storage/account.rs (L62-73)
```rust
/// Returns raw supply positions, defaulting to an empty map.
pub(crate) fn get_supply_positions(
    env: &Env,
    account_id: u64,
) -> Map<HubAssetKey, AccountPositionRaw> {
    get_user(env, &ControllerKey::SupplyPositions(account_id)).unwrap_or_else(|| Map::new(env))
}

/// Returns raw debt positions, defaulting to an empty map.
pub(crate) fn get_debt_positions(env: &Env, account_id: u64) -> Map<HubAssetKey, DebtPositionRaw> {
    get_user(env, &ControllerKey::BorrowPositions(account_id)).unwrap_or_else(|| Map::new(env))
}
```

**File:** contracts/controller/src/storage/account.rs (L94-105)
```rust
fn write_side_map<V: TryFromVal<Env, Val> + IntoVal<Env, Val>>(
    env: &Env,
    key: &ControllerKey,
    map: &Map<HubAssetKey, V>,
) {
    let persistent = env.storage().persistent();
    if map.is_empty() {
        persistent.remove(key);
    } else {
        persistent.set(key, map);
    }
}
```

**File:** contracts/controller/src/storage/account.rs (L144-162)
```rust
/// Loads both position maps and current NFT ownership. Missing metadata or
/// unresolved ownership fails with `AccountNotFound`.
pub(crate) fn get_account(env: &Env, account_id: u64) -> Account {
    try_get_account(env, account_id)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AccountNotFound))
}

/// Loads both position maps and current NFT ownership; returns `None` when
/// metadata is absent or ownership cannot be resolved.
pub(crate) fn try_get_account(env: &Env, account_id: u64) -> Option<Account> {
    let meta = try_get_account_meta(env, account_id)?;
    let owner = try_account_owner(env, account_id)?;
    Some(account_from_parts(
        owner,
        meta,
        get_supply_positions(env, account_id),
        get_debt_positions(env, account_id),
    ))
}
```

**File:** contracts/controller/src/storage/account.rs (L164-172)
```rust
/// Loads metadata, current owner, and debt; leaves supply deliberately unloaded.
/// Missing metadata raises `AccountNotInMarket`; unresolved ownership raises
/// `AccountNotFound`. The empty supply map does not prove supply is absent.
pub(crate) fn get_account_borrow_only(env: &Env, account_id: u64) -> Account {
    let meta = get_account_meta(env, account_id);
    let owner = account_owner(env, account_id);
    let borrow_positions = get_debt_positions(env, account_id);
    account_from_parts(owner, meta, Map::new(env), borrow_positions)
}
```

**File:** contracts/controller/src/storage/account.rs (L258-272)
```rust
/// Renews user TTL for each existing account entry; does not renew the NFT.
pub(crate) fn renew_user_account(env: &Env, account_id: u64) {
    let persistent = env.storage().persistent();
    let keys = [
        ControllerKey::AccountMeta(account_id),
        ControllerKey::SupplyPositions(account_id),
        ControllerKey::BorrowPositions(account_id),
        ControllerKey::Delegates(account_id),
    ];
    for key in &keys {
        if persistent.has(key) {
            renew_user_key(env, key);
        }
    }
}
```

**File:** contracts/controller/src/account.rs (L165-170)
```rust
/// Deletes the account and burns its NFT when both position maps are empty.
pub(crate) fn cleanup_account_if_empty(env: &Env, account: &Account, account_id: u64) {
    if account.is_empty() {
        remove_account_and_burn_nft(env, account_id);
    }
}
```
