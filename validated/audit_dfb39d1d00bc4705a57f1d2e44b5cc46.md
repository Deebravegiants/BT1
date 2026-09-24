### Title
Stale launch-time exchange-rate bound lets a devalued LT push graduation LP reserves past `uint112`, permanently bricking `finalizeGraduation` and freezing all curve-raised LT and 250M reserved tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._deployAndSeed` bounds `virtualLtReserve` at launch to `type(uint112).max / 4`, based on the *reasoning* that the maximum LT the curve can ever raise is `3 × virtualLtReserve` (curve sell-out) [1](#0-0) . That bound is computed once, using the LT's `exchangeRate()` **at launch time** [2](#0-1) . But the actual graduation trigger is a **USD**-denominated threshold evaluated against the LT's **live, current** `exchangeRate()` — `(storedAssetReserve − virtualLtReserve) × exchangeRate ≥ $9K` [3](#0-2) . If the LT is a leveraged/rebasing asset whose `exchangeRate` can fall materially after launch (leverage cuts both ways), the amount of raw LT that must be raised to reach the fixed `$9K` USD threshold grows inversely with the drop in rate — unboundedly, since nothing re-checks the uint112 assumption against the current rate before or during graduation.

### Finding Description
1. At launch, `virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate` is derived from the **launch-time** exchange rate, and is bounded to `type(uint112).max / 4` under the assumption that raised LT peaks at `3 × virtualLtReserve` [4](#0-3) . This bound is never re-validated later.
2. The graduation USD trigger is computed with the LT's *live* `exchangeRate()`, not the launch-time rate [5](#0-4) . If the LT devalues after launch (e.g., a leveraged token losing value from adverse price moves in its underlying), a much larger quantity of raw LT tokens is required to reach the same fixed `$9K` threshold than the `3 × virtualLtReserve` figure the uint112 guard assumed.
3. `ltFromPair = assetReserve − virtualLtReserve` is later used, unclamped by any uint112-aware cap, to seed the real HyperSwap V2 pair as one of the two `addLiquidity`/`mint` amounts in `finalizeGraduation` → `_seedUniswapV2Direct` [6](#0-5) .
4. Standard UniswapV2/HyperSwap V2 pairs store reserves as `uint112` and truncate/overflow silently on `_update`/`mint` if the deposited amount, combined with existing reserves, exceeds `type(uint112).max`. Because the launch-time bound check in `_deployAndSeed` no longer reflects reality by the time graduation happens, `ltFromPair` can exceed the pair's `uint112` reserve slot, corrupting the seeded pool's reserves (silent wraparound in the V2 pair, not a Solidity-level revert, since the truncation happens inside the external HyperSwap V2 pair contract's own `uint112` casting, which is out of alt.fun's control).
5. This is functionally the same bug class as the PyCA `cryptography` overflow: a size/amount check performed once against an assumption that becomes stale as the underlying value (buffer size / exchange rate) changes, allowing values to grow past the fixed-width integer boundary the code relies on for correctness.

### Impact Explanation
If `ltFromPair` or `tokensForLP` overflow the destination `uint112` slot when seeded into the real HyperSwap pair, the graduation liquidity is seeded at a corrupted, essentially arbitrary ratio — this is a permanent freezing/loss of value for: the curve's raised LT (all of it, since `Router.graduate` has already drained it into `Bonding` before the seed step, and `LPLock.recordLock` is one-shot and cannot be re-run), the 250M reserved tokens, and the price integrity of the newly-opened LP that all post-graduation traders rely on. Because `finalizeGraduation` is permissionless and expected to "never revert under any pre-seed shape" per design intent [7](#0-6) , a wraparound rather than a revert is the worst possible outcome — the funds get irrevocably locked into a mispriced/broken pool instead of the transaction simply failing safely.

### Likelihood Explanation
This requires a real-world drop in the paired LT's `exchangeRate()` between token launch and that token's graduation, large enough that the USD-threshold-implied raw LT amount exceeds 4x the launch-time bound (`type(uint112).max/4` headroom). Given that `alt.fun` explicitly pairs against externally-managed, leveraged BounceTech LTs whose `exchangeRate` can move in either direction over the token's lifetime, and that the graduation threshold is fixed in USD terms (not LT terms), this is a plausible economic/market scenario rather than a purely theoretical one, though it requires a specific and fairly extreme devaluation to actually breach the guard's 4x headroom.

### Recommendation
Re-validate the `uint112` headroom against the pair's *live* `exchangeRate()` immediately before `_prepareGraduationLiquidity`/`finalizeGraduation` seeds the HyperSwap pair (not just once at launch), and revert (rather than silently seed) if `ltFromPair` or `tokensForLP` would exceed a safe fraction of `type(uint112).max`. Alternatively, clamp `ltFromPair` deposited into the V2 pair to a value provably safe for `uint112`, and route any excess through the existing `Router.graduate`/sweep-to-owner path instead of the LP mint.

### Proof of Concept
Not independently reproduced in a local Foundry test within this scan — this analysis is based on static code review of `Bonding._deployAndSeed`'s uint112 guard and the live-exchange-rate USD trigger. A concrete PoC would require: (1) launching a token against a mock LT starting at a high `exchangeRate`, (2) crashing the mock's `exchangeRate()` well below launch-time levels before the curve reaches its USD threshold, (3) buying to trigger graduation, and (4) asserting that `p.ltFromPair` computed in `_prepareGraduationLiquidity` exceeds `type(uint112).max`, or that the resulting HyperSwap pair reserve read back via `getReserves()` no longer matches the deposited amount (indicating truncation). This exact scenario was not run against the repository's test suite in this session, so the numeric feasibility (whether realistic LT devaluation ranges can actually breach the 4x headroom given `VIRTUAL_LIQUIDITY_USD` and the `$9K` graduation threshold's relative magnitudes) is not fully confirmed and should be validated with `test/GraduationInvariants.t.sol`-style fuzzing before treating this as certain.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-494)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
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

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** docs/contracts-scope.md (L68-70)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
```

**File:** packages/contracts/AGENTS.md (L86-86)
```markdown
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/AGENTS.md (L88-88)
```markdown
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
