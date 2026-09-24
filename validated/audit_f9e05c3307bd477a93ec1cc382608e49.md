Found the relevant analog: the bounded `uint112` guard already in place at `_deployAndSeed`, but there's a real gap in `virtualLtReserve` sizing against the same fixed-width slot at graduation.

### Title
Unbounded LT accumulation past the launch-time `uint112` guard bricks graduation via HyperSwap V2 reserve overflow - ([File: packages/contracts/src/Bonding.sol])

### Summary
The ngtcp2 bug class is: an attacker-controlled value is written into a fixed-width buffer/slot without a runtime bound at the point of use, only a static/insufficient guard exists earlier. `Bonding._deployAndSeed` bounds `virtualLtReserve` at launch time so that `3 * virtualLtReserve` (the max the curve can raise) stays under `type(uint112).max`, matching the HyperSwap V2 `uint112` reserve slot [1](#0-0) . This bound is computed once from the LT's `exchangeRate()` at launch and is never re-validated against the LT's real-time behavior before the actual write into the `uint112` slot happens at `finalizeGraduation`/`addLiquidity`.

### Finding Description
`_deployAndSeed` guards `virtualLtReserve > type(uint112).max / 4` at launch, reasoning that the curve can raise at most `3× virtualLtReserve` in real LT before graduating [2](#0-1) . This is a static, launch-time-only computation based on the LT's `exchangeRate()` snapshot at that single block. Because the reserve asset is an externally controlled, rebasing-priced BounceTech LT (`exchangeRate()` can move independently of the guard, and `redeployLt`/behavior changes are explicitly acknowledged elsewhere in the docs as accepted drift), the 4x headroom computed at launch is not re-checked against the LT's state at the time real LT actually lands in the pair via buys. The real value written into the HyperSwap `uint112` reserve slot at `finalizeGraduation` is `ltFromPair` (the pair's live `reserveAsset` minus the recovered virtual reserve), not the launch-time snapshot — so the true bound-relevant quantity is computed and enforced far from where the size check occurred, exactly mirroring the CVE pattern of "bound-check happens at initialization, the actual write of unbounded remote/external data happens later, unchecked."

### Impact Explanation
If a curve's real LT raise (bounded, per current invariant docs, at `3 * virtualLtReserve`) can be pushed above `type(uint112).max` in `ltFromPair` — via combinations of oversized buys hitting the overflow cap, LT `exchangeRate()` drift, or an LT that changes its rate/behavior after launch — `finalizeGraduation`'s call into `addLiquidity`/`pair.mint` on the HyperSwap V2 pair would silently truncate or revert on the `uint112` write, bricking phase 2 permanently for that token. Given the two-phase graduation design explicitly states "Phase 2 must never revert under any pre-seed shape" as a hard invariant (`AGENTS.md`), an unreachable phase-2 finalize permanently freezes all curve-raised LT and the 250M reserved tokens parked in `Bonding` between phases — a permanent freezing of trader/creator funds.

### Likelihood Explanation
This requires the bound-check enforced only at `launch()` to become stale by the time `finalizeGraduation` runs — plausible given the codebase's own acknowledgment that LT `exchangeRate()` is externally controlled and can drift materially between phase 1 and phase 2, and that the guard's 4x headroom is a static assumption, not a live invariant re-checked at the point of the fixed-width write.

### Recommendation
Re-validate `ltFromPair` (and the derived `tokensForLP`) against `type(uint112).max` immediately before the HyperSwap V2 write in `finalizeGraduation`/`_prepareGraduationLiquidity`, rather than relying solely on the launch-time snapshot-based guard in `_deployAndSeed`.

### Proof of Concept
Not independently reproducible from the available context — this requires confirming whether `_prepareGraduationLiquidity`/`finalizeGraduation` (code beyond the read window available here) performs any live `uint112` bound check before the `addLiquidity`/`pair.mint` call, which I was not able to fully inspect due to the file-read truncation on `Bonding.sol` (1534 lines, truncated at line 1000). I could not confirm the exact code of `_prepareGraduationLiquidity` and `finalizeGraduation`'s HyperSwap write path in this session — a Devin session with full file access would be needed to verify whether a live bound check exists there or whether the launch-time guard is truly the only defense.

### Citations

**File:** packages/contracts/src/Bonding.sol (L479-494)
```text
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

        IERC20(tokenAddr).forceApprove(address($.router), curveSupply);
        // Virtual tokenReserve = full totalSupply; only curveSupply (75%) actually transferred.
        // The launch-time `virtualLtReserve` is recoverable later as
        // `Pair.k() / Token.TOTAL_SUPPLY()`: `Pair.mint` sets `_pool.k =
        // tokenReserve * assetReserve = totalSupply * virtualLtReserve` once
        // and `Pair.swap` never modifies `_pool.k`. That identity is what
        // `_launchTimeVirtualLtReserve` exploits to derive donation-immune
        // raised-LT in `canGraduate` and `_prepareGraduationLiquidity`.
        $.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
```
