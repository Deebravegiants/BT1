### Title
Archived persistent market state permanently bricks a market and freezes all user funds - (File: contracts/pool/src/storage.rs)

### Summary
The WDDX NULL-pointer-dereference class maps onto this codebase as a read of absent state that unconditionally panics. Every pool operation loads `PoolKey::Params` / `PoolKey::State` from Soroban **persistent** storage via `read_params` / `read_state`, which `unwrap_or_else` into `GenericError::PoolNotInitialized` — and even before reaching that code, a read of an archived persistent entry makes the host abort the call. TTL renewal only happens *inside* `load_state`/`renew_market` on a successful access, so a market whose entries expire is unrecoverable through the contract.

### Finding Description
`read_params` and `read_state` fetch `PoolKey::Params(hub_asset)` and `PoolKey::State(hub_asset)` from `env.storage().persistent()` and panic if the key is absent (contracts/pool/src/storage.rs:23-38). `load_state`/`load_sync_data` renew the TTL *after* the read succeeds (lines 41-53), so renewal is self-serve only while the entry is still live.

Every unprivileged entrypoint in scope funnels through this load: `ops::renewed_market` is called at the top of `flash::prepare` (contracts/pool/src/ops/flash.rs:79) and equivalently by supply/borrow/withdraw/repay/liquidate paths in the controller/pool. Once a market's persistent entries pass archival without being touched, every subsequent call that touches that `(hub, asset)` aborts on the expired-entry host error — there is no restore path in the load functions, and the panic maps to a permanently unreachable market rather than a clean, recoverable error.

This is structurally identical to CVE-2016-9934: a dereference of state that is absent yields a hard crash (NULL deref / host abort on archived key), converting missing data into a denial of service.

### Impact Explanation
Permanent freezing of funds. Once `PoolKey::Params`/`PoolKey::State` for a market archives, `supply`, `withdraw`, `repay`, `borrow`, `liquidate`, `flash_loan`, `claim_revenue`, and `recapitalize` for that `(hub_id, asset)` all revert unconditionally. All supplier principal, accrued yield, and bad-debt-recoverable collateral in that market become unreachable through any listed entrypoint, since none offer an alternative storage path or an explicit `restore` of archived entries.

### Likelihood Explanation
The trigger does not require privilege, only that a low-activity market's persistent entries outlive their TTL (`TTL_BUMP_SHARED` window in common/src/constants.rs). A user can accelerate the condition by creating dust positions in an obscure hub/asset pair and letting it sit; more realistically it hits naturally on thin markets. The impact is unconditional once expiry occurs — no oracle, price, or race dependency — so for any market that lapses, loss of all market funds is certain. Rated High impact; likelihood constrained by the need for a full TTL window of zero interaction (partial renewal by any single touch resets the clock), placing this at Medium overall.

### Recommendation
- Add a contract entrypoint (or fold into `read_params`/`read_state` callers) that invokes `env.storage().persistent().extend_ttl`/`restore` semantics so archived `PoolKey::Params`/`PoolKey::State` can be resurrected via Soroban's restore transaction rather than reverting forever.
- Alternatively, keep market-critical params/state in instance storage (permanent, contract-lifetime) since archival of per-market persistent state converts a passive liveness lapse into permanent fund loss.
- Emit a pre-expiry warning invariant: renewal currently only runs after a successful read; move `renew_market` ahead of `read_state` where host semantics allow, and document the operational requirement that every live market must be touched within `TTL_BUMP_SHARED` ledgers.

### Proof of Concept
1. Admin configures market `(hub_id = H, asset = A)`; a supplier calls `supply` depositing `X` units of `A`. `PoolKey::Params(H,A)` and `PoolKey::State(H,A)` are written to persistent storage with TTL `TTL_BUMP_SHARED`.
2. No transaction touches `(H,A)` for longer than the TTL window (achievable by any single unprivileged dust supplier on an inactive market).
3. Any user calls `withdraw`, `repay`, `liquidate`, or `flash_loan` on `(H,A)`. `ops::renewed_market` → `read_params`/`read_state` hits the archived `PoolKey::Params(H,A)` entry at contracts/pool/src/storage.rs:26/36; the host aborts on the expired persistent key (or `PoolNotInitialized` after eviction), reverting the call.
4. Repeat for every entrypoint — all revert identically. Supplier funds in `A` under `(H,A)` are permanently frozen; `recapitalize` cannot route around the missing params since it loads the same keys. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/pool/src/storage.rs (L23-45)
```rust
pub(crate) fn read_params(env: &Env, hub_asset: &HubAssetKey) -> MarketParamsRaw {
    env.storage()
        .persistent()
        .get(&PoolKey::Params(hub_asset.clone()))
        .unwrap_or_else(|| panic_with_error!(env, GenericError::PoolNotInitialized))
}

/// Loads market state, or panics if the market was never created.
///
/// Does not extend the TTL; [`load_state`] does.
pub(crate) fn read_state(env: &Env, hub_asset: &HubAssetKey) -> PoolStateRaw {
    env.storage()
        .persistent()
        .get(&PoolKey::State(hub_asset.clone()))
        .unwrap_or_else(|| panic_with_error!(env, GenericError::PoolNotInitialized))
}

/// Loads market state and extends the TTL of both params and state keys.
pub(crate) fn load_state(env: &Env, hub_asset: &HubAssetKey) -> PoolStateRaw {
    let state = read_state(env, hub_asset);
    renew_market(env, hub_asset);
    state
}
```

**File:** contracts/pool/src/ops/flash.rs (L76-80)
```rust
pub(crate) fn prepare(env: &Env, hub_asset: HubAssetKey, amount: i128) -> Cache {
    require_positive_amount(env, amount);

    let cache = ops::renewed_market(env, &hub_asset);
    assert_with_error!(
```

**File:** common/src/validation.rs (L30-33)
```rust
#[inline]
pub fn expect_invariant<T>(env: &Env, opt: Option<T>) -> T {
    opt.unwrap_or_else(|| panic_with_error!(env, GenericError::InternalError))
}
```
