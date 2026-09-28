### Title
Unprivileged attacker can flash-inflate utilization at accrual time to fake borrow demand and pump the supply index - (File: contracts/controller/src/strategies/flash_position.rs, contracts/pool/src/interest.rs)

### Summary
The Dutch-auction bug class is "a participant runs the mechanism untruthfully by creating artificial demand at near-zero cost, inflating perceived value and extracting profit." XOXNO Lending has the same shape: `flash_position` mints arbitrarily large pool debt **before** the receiver callback, with **no flash fee**, so an attacker can hold fake borrow "demand" on the pool ledger while forcing `update_indexes` to accrue the entire elapsed interval at a utilization spike, inflating the supply index and letting the attacker withdraw supply shares for more underlying than is backed.

### Finding Description
Interest accrual in `accrue_chunk` reads the pool's live aggregate state — `cache.borrowed()` and `cache.supplied()` — to determine the rate applied to the whole elapsed interval (`delta_ms`, chunked by `MAX_COMPOUND_DELTA_MS`) [1](#0-0) . The utilization input to `accrue_step` is therefore whatever `borrowed` is at the instant accrual runs, not a time-weighted average.

`flash_position` mints `amount` of debt onto the account at the pool level (`create_strategy`-style debt mint, no origination fee), then calls `execute_flash_position` on an arbitrary attacker-controlled `receiver` contract, and only checks account solvency afterward. During that callback the minted debt sits in the pool's `borrowed` aggregate. If the attacker's receiver (or any other contract reached in the callback's auth tree) invokes the permissionless `controller.update_indexes(hub_assets)` for the same market, the pool accrues the full interval since the last accrual at the spiked utilization — i.e., near the kinked model's maximum borrow rate — and bakes the resulting jump into `borrow_index`/`supply_index` permanently.

The attacker, who already holds supply shares in the market, then unwinds: the flash position closes (or stays as a real leveraged position), and the attacker calls `withdraw` to redeem supply shares at the inflated `supply_index`. The surplus comes out of tracked `cash`/`supplied` backing belonging to other suppliers — classic dilution, identical in spirit to an auctioneer bidding early to inflate the clearing price and withdrawing proceeds.

The "near-zero cost" property also maps: `flash_position` charges no fee for the minted debt, so the fake demand costs nothing beyond gas and the collateral callback leg.

### Impact Explanation
Theft of user funds / unclaimed yield. The supply index is inflated for all suppliers, but the attacker alone chooses to enter and exit around the manipulation. Their withdrawal is paid from pool `cash`; the inflated index claim exceeds real accrued interest, so other suppliers and the protocol absorb the shortfall (eventual `PoolInsolvent`/`InsufficientLiquidity` conditions on honest withdrawals). Repeated cycles compound the drain. Magnitude scales with the un-accrued interval (`elapsed_ms`) and the rate-model maximum, and the attacker can time it for long gaps since the last accrual, and/or run it on several markets via the `Vec<HubAssetKey>` argument.

### Likelihood Explanation
Requires a market where the attacker holds supply and a meaningful gap since last accrual — both routinely available on any listed market. The attack is atomic, uses only documented unprivileged entrypoints (`flash_position` with an attacker receiver contract, `update_indexes`, `withdraw`), and costs no flash fee. One caveat I could not fully verify within scope: whether `controller.update_indexes` passes through `require_not_flash_loaning` during an ongoing flash (the guard is enforced inside `require_authorized_caller` and similar paths [2](#0-1) ); if `update_indexes` lacks that check, the mid-callback variant works. Even if guarded there, a weaker non-flash variant exists: the attacker keeps a large real borrow open so `update_indexes` accrues at elevated utilization — same root cause (instantaneous-utilization rate applied retroactively to elapsed time), at higher but bounded cost.

### Recommendation
- Apply `require_not_flash_loaning` (or equivalent `with_flash_guard` coverage) to `controller.update_indexes` and any other entrypoint that triggers pool accrual, so accrual can never observe flash-minted debt.
- More robustly, compute utilization for accrual from state excluding transient flash mints, or accrue indexes *before* minting flash debt inside `flash_position`/`create_strategy` so the spike cannot be retroactively applied to elapsed time.
- Cap per-accrual index movement, or time-weight utilization (accumulate rate × dt continuously) rather than applying current utilization to the whole gap.

### Proof of Concept
1. Attacker supplies asset `A` in market `(hub, A)` to account `S`, obtaining supply shares.
2. Wait until `get_delta_time(hub, A)` is large.
3. Attacker deploys receiver contract `R` implementing `execute_flash_position`.
4. Call `controller.flash_position(caller, account_id: 0, spoke_id, mode, debt = (hub, B), amount = huge, receiver = R, collaterals = [enough A to stay solvent])`. The pool mints `huge` debt of `B` in the same market's utilization surface (or use `B = A` market where permitted so utilization spikes directly).
5. Inside `R.execute_flash_position`, invoke `controller.update_indexes([ (hub, A) ])`. `accrue_chunk` computes the rate from `cache.borrowed()` which now includes the flash debt; utilization ≈ 1, so the max model rate is applied to the full elapsed interval; `supply_index` jumps.
6. Callback returns; solvency check passes because declared collateral was posted.
7. Attacker calls `withdraw(caller, S, [(hub, A), amount = 0])`, redeeming all supply shares at the inflated index — receiving more `A` than deposited plus legitimately accrued interest.
8. Optionally unwind/repay the flash position normally; net profit is the index-inflation surplus drained from `cash`.

### Citations

**File:** contracts/pool/src/interest.rs (L39-53)
```rust
fn accrue_chunk(env: &Env, cache: &mut Cache, delta_ms: u64) {
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
    );

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
}
```

**File:** contracts/controller/src/risk/validation.rs (L13-25)
```rust
pub(crate) fn require_authorized_caller(env: &Env, caller: &Address) {
    caller.require_auth();
    require_not_flash_loaning(env);
}

/// Rejects execution while the temporary flash-loan flag is set.
pub(crate) fn require_not_flash_loaning(env: &Env) {
    assert_with_error!(
        env,
        !storage::is_flash_loan_ongoing(env),
        FlashLoanError::FlashLoanOngoing
    );
}
```
