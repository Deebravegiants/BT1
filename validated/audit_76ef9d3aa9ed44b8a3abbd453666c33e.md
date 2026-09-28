### Title
Permissionless `force_socialize_bad_debt` bypasses the owner-only gate and forces bad-debt socialization on any insolvent account - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The controller exposes two bad-debt cleanup gates: a permissionless dust-capped gate (`clean_bad_debt`) and an owner-only uncapped gate (`force_socialize_bad_debt`). The code documents `BadDebtGate::InsolventOnly` as "Owner-only," but `process_force_socialize_bad_debt` performs no authentication and no ownership check at all — it only rejects calls during a flash loan. Any unprivileged address can therefore force-socialize an insolvent account's debt with no dust cap on the residual collateral, burning the account's remaining collateral and writing down the market's supply index ahead of the owner's intent.

### Finding Description
`process_clean_bad_debt` correctly models the permissionless path: it requires `caller.require_auth()` and then applies `BadDebtGate::DustCapped`, admitting cleanup only when the insolvent account's collateral is at or below the dust threshold. [1](#0-0) 

`BadDebtGate` explicitly distinguishes the two admission policies, labeling `InsolventOnly` as "Owner-only: insolvent alone, with no cap on the collateral left behind." [2](#0-1) 

However `process_force_socialize_bad_debt` enforces only `require_not_flash_loaning` before invoking `socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly)` — there is no `require_auth` on a meaningful owner identity and no `require_account_owner`/`require_owner_or_delegate` check against `account_id`. [3](#0-2) 

Contrast with every other position-mutating entrypoint, which authenticates the caller and verifies ownership or delegation (e.g., `process_withdraw` calls `require_owner_or_delegate` against the loaded account). [4](#0-3) 

`socialize_bad_debt` then admits cleanup on the weak predicate `total_debt > total_collateral` — with no dust cap — and calls `bad_debt::execute_bad_debt_cleanup`, which seizes the residual collateral and writes down the supply index, socializing the shortfall across all suppliers of the market. [5](#0-4) 

### Impact Explanation
This is an incorrect-authorization bug reachable by any unprivileged address via the public `force_socialize_bad_debt` controller entrypoint:

- **Owner harm:** For an insolvent account whose residual collateral exceeds the dust cap, the owner's intended privilege is to choose when (or whether, e.g., after partial repayment or collateral top-up) to socialize. A third party can invoke the cleanup at the moment the account first dips below water, destroying residual collateral that a price bounce, a voluntary `repay`, or an added `supply` leg could have preserved — permanent loss of the user's remaining funds.
- **Supplier harm:** `execute_bad_debt_cleanup` writes down the market supply index, realizing a loss across all suppliers of that `(hub, token)` book. Forcing this prematurely and on the caller's timing lets an attacker pick the worst moment (e.g., immediately after a transient price dip while index accrual is stale), converting a recoverable shortfall into a permanent, protocol-wide write-down — theft of user funds / realized protocol insolvency on the attacker's schedule rather than the owner's.

### Likelihood Explanation
The trigger condition is merely `total_debt > total_collateral`, a state every lending market can enter transiently during sharp price moves or oracle updates. The attacker needs only a single `force_socialize_bad_debt(account_id)` call — no capital, no flash loan, no delegate grant — and it is explicitly designed to be reachable by the keeper/permissionless surface (`require_not_flash_loaning` is the only guard), so it is available to any address at any time. The only mitigation is that the account must already be insolvent; nothing else gates the caller.

### Recommendation
Authenticate the account owner in `process_force_socialize_bad_debt` before applying `BadDebtGate::InsolventOnly`, matching the documented owner-only policy:

```rust
pub(crate) fn process_force_socialize_bad_debt(env: &Env, caller: Address, account_id: u64) {
    caller.require_auth();
    account::require_account_owner(env, account_id, &caller);
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

Alternatively, if the intent is genuinely permissionless cleanup, drop the `InsolventOnly` gate distinction and the "Owner-only" documentation — but then re-evaluate whether removing the dust cap for arbitrary callers is acceptable, since it materially weakens the collateral-preservation window for insolvent accounts.

### Proof of Concept
1. Victim account `A` holds supply in market `M` and debt such that, after a price move, `total_debt > total_collateral`, but residual collateral is well above the dust threshold (so `clean_bad_debt` would revert with `CannotCleanBadDebt`).
2. Victim intends to `repay`/`supply` to recover solvency, or to trigger the owner-only force-socialize at a time of their choosing.
3. Unprivileged attacker calls `controller.force_socialize_bad_debt(A)`:
   - `require_not_flash_loaning` passes (no flash loan active); no owner check exists.
   - `socialize_bad_debt` admits via `BadDebtGate::InsolventOnly` since `total_debt > total_collateral`.
   - `execute_bad_debt_cleanup` seizes A's residual collateral and writes down `M`'s supply index.
4. Result: A's remaining collateral is destroyed and all suppliers of `M` absorb the realized shortfall immediately — an outcome reserved by the code's own documentation for the account owner, executed here by an arbitrary address.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L196-199)
```rust
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L202-209)
```rust
/// Admission condition for bad-debt socialization.
#[derive(Clone, Copy, PartialEq)]
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-238)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L245-249)
```rust
/// Socializes debt exceeding collateral without a dust cap, outside flash loans.
pub(crate) fn process_force_socialize_bad_debt(env: &Env, account_id: u64) {
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

**File:** contracts/controller/src/positions/supply.rs (L147-150)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);
```
