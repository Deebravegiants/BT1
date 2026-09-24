### Title
`Bonding.triggerGraduation` bypasses the anti-snipe launch trading delay enforced by `Bonding.buy` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.triggerGraduation` is a permissionless, standalone entry point that replays the same lifecycle transition (`_enterGraduating`) that the normal `buy()` path triggers inline, but it deliberately omits the `LAUNCH_TRADING_DELAY_BLOCKS` anti-snipe gate that `buy()` enforces via `_enforceLaunchDelay`. This mirrors the GraphQL-WebSocket advisory's root cause: a second entry point into the same state machine that skips a security check the primary, middleware-guarded path enforces.

### Finding Description
`Bonding.buy` is gated by `LAUNCH_TRADING_DELAY_BLOCKS` (3 blocks) so that only the creator's seed buy — via a one-shot transient-storage bypass flag set in `launch()` — can trade before `launchBlock + 3`, preventing snipers from front-running price discovery [1](#0-0) .

`triggerGraduation`, however, is exposed as an unconditional, unprivileged external function that performs the identical `Curve → Graduating` transition (`_enterGraduating`) without going through `buy()` or its delay check at all [2](#0-1) . The developer's own comment on the function acknowledges the omission explicitly and justifies it only by asserting that `canGraduate` cannot return `true` "from a fresh launch within the delay window" [3](#0-2) .

That assumption rests entirely on the curve's USD value staying below `GRADUATION_THRESHOLD_USD` during the delay window. But per the contract's own design, the curve's USD valuation is derived by combining the stored/virtual reserves with the **live** `exchangeRate()` of the external, rebasing-priced BounceTech LT reserve asset — not a value fixed at launch. If the LT's exchange rate moves sharply (a rebase, an oracle update, or any price action on the LT itself) within the 3-block delay window, `canGraduate` can become `true` purely from LT price movement, with zero real curve buys having occurred. In that case, an unprivileged caller can invoke `triggerGraduation(tokenAddress)` during the anti-snipe window that `buy()` would otherwise block, locking in `_prepareGraduationLiquidity`'s LP-bound amounts at a curve state that never underwent the intended price-discovery delay.

### Impact Explanation
A successful bypass allows the two-phase graduation (`triggerGraduation` → `finalizeGraduation`) to run and permanently seed the HyperSwap V2 TOKEN/LT pair and lock LP via `LPLock.recordLock` before the anti-snipe delay has elapsed and before organic trading has set a fair curve-close price. This freezes creator/trader outcomes to a price shaped by external LT volatility rather than genuine demand, and — because `_prepareGraduationLiquidity` never re-reads `exchangeRate()` — that mis-timed price becomes irreversibly baked into the LP once phase 2 finalizes, i.e. an LP seeded away from the intended curve close.

### Likelihood Explanation
Reachability depends on the LT's `exchangeRate()` moving enough within a 3-block window to cross the USD threshold with only virtual reserves in play — a condition outside the Bonding contract's control since the LT is an external, live-priced instrument the report class explicitly flags as attacker-relevant ("a reserve asset that is an external rebasing-priced LT read live via exchangeRate"). This is plausible but not guaranteed on every launch, so likelihood is contingent on LT volatility characteristics at launch time, which I could not fully verify from `canGraduate`'s exact implementation within this review.

### Recommendation
Enforce the same `LAUNCH_TRADING_DELAY_BLOCKS` check inside `triggerGraduation` (or a shared internal guard used by both `buy()` and `triggerGraduation()`), or explicitly re-derive `canGraduate`'s dependency on launch-time-frozen reserves rather than the live `exchangeRate()` for any graduation check reachable before the delay elapses.

### Proof of Concept
1. Creator calls `launch()`, seed buy executes at block N via the transient bypass flag.
2. Within blocks N+1..N+3 (before `buy()` would allow any public trade), the underlying LT's `exchangeRate()` moves such that the curve's virtual-reserve USD valuation crosses `GRADUATION_THRESHOLD_USD` (via rebase/price update on the LT, outside Bonding's control).
3. An unrelated address calls `Bonding.triggerGraduation(tokenAddress)` — no buy, no delay check — and `canGraduate` returns true, entering `Lifecycle.Graduating` [4](#0-3) .
4. `finalizeGraduation` is subsequently called permissionlessly, seeding the V2 LP and calling `LPLock.recordLock`, permanently fixing the LP at a price that reflects only virtual reserves and the LT's transient rate — never the delay-protected organic curve price.

### Citations

**File:** packages/contracts/src/Bonding.sol (L116-135)
```text
    /// @notice Anti-snipe trading delay. After `launch()`, public buys on the
    ///         curve are blocked for `LAUNCH_TRADING_DELAY_BLOCKS` blocks (so
    ///         trading opens at `launchBlock + LAUNCH_TRADING_DELAY_BLOCKS + 1`).
    ///         The seed buy attached to the launch tx bypasses the gate via
    ///         the transient flag set in `launch()` — see `buy()` for the
    ///         consume-once mechanic. Combined with `Zap.MIN_SEED_USDC`, this
    ///         is the system's first-block-sniper mitigation: no other buyer
    ///         can race the creator into block N or pile in at N+1..N+3. The
    ///         gate is buy-only and does not lock the seed in — see
    ///         `_enforceLaunchDelay`.
    uint256 public constant LAUNCH_TRADING_DELAY_BLOCKS = 3;

    /// @dev Transient-storage slot keying the seed-buy bypass. Set in
    ///      `launch()` to the freshly-deployed token address, consumed by the
    ///      first matching `buy()` call in the same tx (i.e. the seed buy
    ///      Zap fires immediately after launch). Naturally cleared at
    ///      end-of-tx, so it cannot leak across txs even if a bug skips the
    ///      consume. Keyed off a domain-separated label to avoid collisions
    ///      with any future transient slots elsewhere in the contract.
    bytes32 private constant _SEED_BUY_BYPASS_SLOT = keccak256("alt-fun.bonding.seedBuyBypass.v1");
```

**File:** packages/contracts/src/Bonding.sol (L955-979)
```text
    /// @notice Permissionless trigger for phase 1 of graduation. Same flow as
    ///         the inline post-buy trigger inside `_executeBuy`, but callable
    ///         without any buy. Closes the case where `canGraduate` is true
    ///         (LT appreciation pushed the curve past the USD threshold) but
    ///         the closing buy on the curve would mint below the BounceTech
    ///         LT mint floor and revert with `BelowMinTransactionSize`,
    ///         making the token un-graduatable via `Zap.buy`.
    /// @dev    `_enterGraduating` reads pair reserves and the launch-time
    ///         virtual reserve only — it does not depend on a buy having
    ///         just landed, so the same logic is safe to expose as a
    ///         standalone entry point. The lifecycle pre-checks mirror
    ///         `Bonding.buy`; the launch trading delay is intentionally
    ///         not enforced because `canGraduate` already requires either
    ///         the USD threshold or full curve sellout, both of which are
    ///         unreachable from a fresh launch within the delay window.
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```
