### Title
Missing owner authorization in `force_socialize_bad_debt()` lets any address bypass the dust cap and socialize arbitrarily large insolvent positions - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The controller exposes two bad-debt cleanup paths with different intended admission rules. `process_clean_bad_debt` is permissionless but bounded by a dust cap on remaining collateral (`BadDebtGate::DustCapped`). `process_force_socialize_bad_debt` is documented as the owner-only variant with no collateral cap (`BadDebtGate::InsolventOnly`), but the implementation performs **no authorization at all** — it neither calls `require_auth` on the account owner nor `require_owner_or_delegate`. Any unprivileged address can invoke it against any insolvent account, unconditionally seizing all of its collateral and writing the debt down to suppliers, entirely bypassing the normal liquidation flow.

### Finding Description
In `contracts/controller/src/positions/liquidation/mod.rs`:

```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}
```

versus:

```rust
/// Socializes debt exceeding collateral without a dust cap, outside flash loans.
pub(crate) fn process_force_socialize_bad_debt(env: &Env, account_id: u64) {
    validation::require_not_flash_loaning(env);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

The `BadDebtGate` enum itself documents the intended split:

```rust
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}
```

But `process_force_socialize_bad_debt` takes no `caller`/`owner` argument and never reaches `account::require_owner_or_delegate` or `require_account_owner` — the "Owner-only" gate is enforced nowhere. `socialize_bad_debt` only asserts `total_debt > total_collateral`, then `execute_bad_debt_cleanup` seizes every supply position via `pool_seize_positions_call`, releases spoke usage, removes the account, and burns its NFT (`remove_account_and_burn_nft`).

This is structurally the same class as the reference finding: `unstake()` was supposed to carry a precondition (vesting elapsed) distinguishing it from the destructive `rageQuit()` path, but ended up identical to it. Here, the uncapped destructive path was supposed to carry a precondition (account-owner authorization) distinguishing it from the bounded permissionless cleanup, but the precondition was never wired up.

### Impact Explanation
Two consequences follow from the missing gate:

1. **Liquidation bypass / forced write-down.** Normally, an insolvent account is handled by `process_liquidation`, where a liquidator repays debt (injecting real tokens into the pool) and receives collateral at a bonus. With `force_socialize_bad_debt`, anyone can instead dump the position into `execute_bad_debt_cleanup`, which seizes collateral into the pool and writes the uncovered debt down against the supply index — i.e., socializes the loss onto suppliers — with no repayment injected at all. An attacker holding supplied positions in other assets (or a competing liquidator who wants to deny the bonus) can force-socialize large insolvent accounts that the dust cap was designed to keep out of this path, converting recoverable debt into supplier write-downs.

2. **Permanent destruction of the position owner's residual claim.** The cleanup seizes *all* remaining collateral positions and burns the account NFT atomically. For an insolvent account the owner cannot withdraw, but the timing and terms of liquidation (bonus curve, share credit, self-liquidation choice) belong to the protocol's designed flow — not to an arbitrary third party pulling a trigger the code labeled owner-only.

### Likelihood Explanation
- **Reachability:** `process_force_socialize_bad_debt` requires only `account_id` and is outside the flash-loan flag — a single unprivileged transaction.
- **Precondition:** any account with `total_debt > total_collateral` under current strict oracle prices. Such accounts exist transiently during price moves before liquidators act — precisely the window where liquidation (with repayment) should occur, and where the attacker can front-run it with socialization.
- **No cost:** the caller repays nothing, supplies nothing, and suffers no risk.

### Recommendation
Gate `process_force_socialize_bad_debt` to the account owner (or delegate), matching the documented `InsolventOnly` intent:

```rust
pub(crate) fn process_force_socialize_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    let account = storage::get_account(env, account_id);
    account::require_owner_or_delegate(env, account_id, caller, &account.owner);
    socialize_bad_debt(env, account_id, BadDebtGate::InsolventOnly);
}
```

Alternatively, if uncapped socialization is meant to be permissionless, enforce the dust cap in both paths or bound the socialized amount — but the current split between the two gates strongly indicates the uncapped variant was meant to be owner-authorized.

### Proof of Concept
1. Alice holds an account that a price move pushes below water: `total_debt > total_collateral` with collateral far above the dust threshold (so `clean_bad_debt` would revert with `CannotCleanBadDebt`).
2. Eve (any address) calls `controller::force_socialize_bad_debt` — no auth on Eve is checked beyond the flash-loan flag.
3. `socialize_bad_debt` passes the `InsolventOnly` gate (`total_debt > total_collateral`), and `execute_bad_debt_cleanup` seizes all of Alice's supply positions to the pool, exits spoke usage, emits `CleanBadDebtEvent`, and burns Alice's NFT.
4. The debt is written down against the supply index — suppliers absorb it — while no liquidator ever repaid the debt. Eve achieved this in one call at zero cost, despite the gate being documented as owner-only.

Note on uncertainty: whether the net supplier loss strictly exceeds what a normal liquidation would produce depends on the seizure/write-down mechanics in the pool (`pool_seize_positions_call` and the supply-index write-down), which I inspected only at the controller layer; the missing-auth deviation from the documented `Owner-only` gate is nonetheless unambiguous in `contracts/controller/src/positions/liquidation/mod.rs`.