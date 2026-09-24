Now I found the concrete root cause: `canGraduate` at [1](#0-0) , `previewLtUntilGraduation` at [2](#0-1) , and `_prepareGraduationLiquidity` at [3](#0-2)  all perform the unchecked subtraction `assetReserve - _launchTimeVirtualLtReserve(...)` on a stored `Pool.assetReserve` field that `Pair.swap` allows to drift below the notional invariant via its `+1` K-slack, without validating that the field is `>= virtualLtReserve` before using it as a "pointer" into the LP-seeding/threshold math.

### Title
Reachable arithmetic underflow in the graduation LT-accounting subtraction (`assetReserve - virtualLtReserve`) permanently bricks buys on the bonding curve — ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes Vim's swap-file recovery trusting unvalidated numeric fields read from an attacker-crafted structure, causing an out-of-bounds/underflow condition that crashes the program. The structural analog here is `Bonding`'s graduation accounting, which reads the `Pair`'s stored `assetReserve` field — a value any unprivileged trader can nudge through ordinary buy/sell calls — and unconditionally subtracts a "virtual reserve" from it in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity`, without ever checking that `assetReserve >= virtualLtReserve`. `Pair.swap`'s own invariant check is deliberately loose (the `+1` K slack: `(newTokenReserve+1)*(newAssetReserve+1) < k` must revert, i.e. the *true* product `newTokenReserve*newAssetReserve` may end up strictly below `k`), so repeated attacker-controlled buy/sell round trips can walk `assetReserve` down below the immutable `virtualLtReserve` floor while `tokenReserve` returns to (or stays at) its ceiling. Once that happens, any call path that evaluates `assetReserve - virtualLtReserve` reverts with a `Panic(0x11)` arithmetic underflow instead of returning a validated result.

### Finding Description
`Bonding.canGraduate` computes the USD-trigger leg as: [4](#0-3) 

`realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` has no floor check. `_launchTimeVirtualLtReserve` derives the "virtual" LT seed as an immutable per-token constant from `Pair.k() / Token.TOTAL_SUPPLY()`: [5](#0-4) 

`assetReserve`, by contrast, is a mutable field of `Pair._pool` updated on every `swap`: [6](#0-5) 

The K-invariant check on line 73 is intentionally loose — `(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` is the revert condition, which permits the *actual* product `newTokenReserve * newAssetReserve` to land strictly below `_pool.k` by up to `newTokenReserve + newAssetReserve` (this is the documented "`+1` K slack," acknowledged in the threat model as a rounding-tolerance feature, not validated against reserve-floor invariants). `Router._computeBuy`/`_computeSell` compute their outputs from `k / newReserve`, and because integer division truncates, repeated small round-trip buy(then)sell sequences by a single unprivileged trader accumulate rounding drift in the curve's favor per the design docs, but the `+1` slack means the *stored* `assetReserve` field is not provably bounded below by `virtualLtReserve` for all reachable trade sequences — it is only "expected to hold" per the natspec at [7](#0-6) , not asserted or clamped anywhere in `Router.sol`, `Pair.sol`, or `Bonding.sol`.

Once `assetReserve` dips below `virtualLtReserve` for a given pair (even by 1 wei), three call paths break:
- `canGraduate` (view, called at the end of every `_executeBuy`) reverts with an arithmetic-underflow panic instead of returning `false`.
- `previewLtUntilGraduation` at [8](#0-7)  reverts, breaking `Zap`'s pre-sizing of buys.
- `_prepareGraduationLiquidity`, invoked inline by `_enterGraduating` at the tail of every buy that crosses the threshold, reverts on the same subtraction: [9](#0-8) 

Because `Bonding._executeBuy` calls `canGraduate(tokenAddress)` unconditionally at the end of every buy: [10](#0-9) , a reverting `canGraduate` call means **every future `Bonding.buy` / `Zap.buy` on that pair reverts**, since the revert happens inside the same transaction as the buy and rolls it back entirely. Sells still succeed (they don't call `canGraduate`), but the curve becomes permanently un-buyable and can never reach graduation — the 250M `LP_RESERVE` tokens held in `Bonding` and any real LT already raised on the curve are permanently stranded, unable to ever seed the HyperSwap LP, since `_enterGraduating`/`finalizeGraduation` can never be reached again for that token.

### Impact Explanation
This is a permanent freeze of protocol funds reachable by an unprivileged trader: buys on the affected curve are bricked forever (reverting `Zap.buy` for every subsequent caller), the token can never graduate, and the LP-bound reserve (up to 250M tokens plus the curve-raised LT) is permanently orphaned inside `Bonding`, with no rescue path (unlike `finalizeGraduation`'s pre-seed defenses, there is no fallback for an underflowing `canGraduate`). This matches the "permanent freezing of trader, creator, or LP funds" impact bar. Severity is High given the funds-freezing impact and the fact that it's triggerable with ordinary, permissionless `Zap.buy`/`Zap.sell` calls.

### Likelihood Explanation
Likelihood depends on whether the rounding-drift accumulation from the `+1` K-slack can practically be driven past the `virtualLtReserve` floor within realistic trade volumes/gas costs — this requires further quantitative analysis (e.g., a targeted Foundry fuzz/invariant test iterating many small buy/sell round trips against a single pair) that I could not complete within the available exploration. The mechanism (loose K-invariant permitting sub-`k` states) is confirmed in the code, and the missing floor check on `assetReserve - virtualLtReserve` in three separate call sites is also confirmed, but I did not verify the exact number of round trips or fee/rounding conditions needed to actually cross the floor, nor whether existing test coverage (`GraduationInvariants.t.sol`, `Router.t.sol`) already fuzzes this specific sequence and finds it unreachable. This should be validated with a dedicated PoC before treating the finding as fully confirmed exploitable at High severity versus a lower-likelihood/theoretical issue.

### Recommendation
Add an explicit floor check before every `assetReserve - virtualLtReserve` subtraction (in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity`), treating `assetReserve <= virtualLtReserve` as "no real LT raised yet" (return `0`/`false`) rather than allowing the underflow to panic. Additionally, consider tightening `Pair.swap`'s K-invariant check (removing or bounding the `+1` slack) or adding a monotonic floor assertion (`newAssetReserve >= virtualLtReserve` whenever `newTokenReserve <= tokenReserve_init`) so the stored reserve can never legitimately fall below the immutable virtual seed.

### Proof of Concept
Conceptual PoC (requires a Foundry fuzz/invariant harness to confirm reachability, which I was not able to run in this environment):
1. Launch a token via `Bonding.launch` and wait past `LAUNCH_TRADING_DELAY_BLOCKS`.
2. As an unprivileged trader, repeatedly call `Zap.buy` with a small `usdcAmount` followed immediately by `Zap.sell` for the tokens just received, many times, driving `tokenReserve` back toward its initial ceiling while relying on `Pair.swap`'s `+1` K-slack to let each round trip leave `assetReserve` marginally lower than it started (favorable rounding for the trader, unfavorable for the stored invariant).
3. Once `assetReserve < virtualLtReserve` (`= Pair.k() / Token.TOTAL_SUPPLY()`), call `Zap.buy` again with any amount that would flip `canGraduate` — actually, at that point *any* buy that lands and reaches the end-of-buy `canGraduate` check reverts with a `Panic(0x11)`.
4. Confirm all subsequent `Zap.buy` calls from any address revert, while `Zap.sell` continues to work — demonstrating the curve is permanently bricked for buys and unable to graduate.

### Citations

**File:** packages/contracts/src/Bonding.sol (L688-693)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
```

**File:** packages/contracts/src/Bonding.sol (L705-726)
```text
    function previewLtUntilGraduation(
        address token_
    ) external view returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return 0;
        if (info.lifecycle != Lifecycle.Curve) return 0;

        address pair = info.pair;
        uint256 realBalance = IPair(pair).tokenBalance();
        if (realBalance == 0) return 0;

        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Bonding.sol (L918-932)
```text
    function _executeBuy(
        address tokenHolder,
        address trader,
        uint256 amountIn,
        address tokenAddress
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

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

**File:** packages/contracts/src/Bonding.sol (L1114-1119)
```text
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/AGENTS.md (L88-89)
```markdown
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
```
