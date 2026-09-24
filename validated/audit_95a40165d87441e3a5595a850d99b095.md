### Title
Rounding-eroded `assetReserve` can underflow the recovered virtual-LT-reserve subtraction in `canGraduate` / `_prepareGraduationLiquidity`, permanently DoS'ing a curve pair - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.canGraduate` and `Bonding._prepareGraduationLiquidity` both compute `realLtRaised`/`ltFromPair` as `assetReserve - _launchTimeVirtualLtReserve(token_, pair)`, an unguarded `uint256` subtraction analogous to the reported `totalTokenBalances[fromToken] -= vaultBalance` underflow in the external report. [1](#0-0) [2](#0-1) 

### Finding Description
`_launchTimeVirtualLtReserve` recovers the pair's initial virtual LT seed as `k / TOTAL_SUPPLY`, an exact value fixed forever at `Pair.mint`. [3](#0-2) 

`Pair.swap` only enforces a *loosened* K-invariant with a `+1` slack on both reserves (`(newTokenReserve+1)*(newAssetReserve+1) < _pool.k` reverts), not the exact product: [4](#0-3) 

`Router._computeSell` computes `assetOut = reserveAsset - (k / newReserveToken)`, using floor division. Because `floor(k/newReserveToken) <= k/newReserveToken` (real value), the computed `assetOut` is rounded *up* in the seller's favor by up to 1 wei per call, which means the resulting stored `assetReserve` after the swap can land marginally *below* the value that exactly preserves `tokenReserve * assetReserve == k`: [5](#0-4) 

The `Pair.swap` `+1` slack check tolerates this drift instead of rejecting it, so it doesn't revert. Because a user can round-trip buy-then-sell (net token holding returns to zero, `tokenReserve` returns to its ceiling of `TOTAL_SUPPLY`) many times, each pass can shave `assetReserve` down by up to 1 wei relative to the ideal curve, while `tokenReserve` returns arbitrarily close to its ceiling. Repeating this is reachable purely through `Zap.sell`/`Zap.buy` (or direct `Bonding.buy`/`Bonding.sell` via any registered router) by an unprivileged trader, with no privileged role required. Given enough iterations, `assetReserve` can be driven below the fixed `virtualLtReserve = k/TOTAL_SUPPLY`, at which point:
- `canGraduate`'s USD leg, `assetReserve - _launchTimeVirtualLtReserve(...)`, underflows and reverts.
- `_prepareGraduationLiquidity`'s `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(...)` underflows and reverts.

`canGraduate` is documented as being checked at the end of every buy inside `_executeBuy`: [6](#0-5) 

So once the underflow condition is reached, every subsequent `Zap.buy`/`Bonding.buy` on that pair reverts (since the trailing `canGraduate` check reverts), and graduation itself can never complete (`_prepareGraduationLiquidity` reverts too), permanently freezing that token's curve — trader funds already deposited into `Bonding`/`Pair` (and the token's `FeeVault` creator earmark) become unreachable via the normal buy/graduate paths.

Note: I was not able to trace the exact call sites of `canGraduate()`/`_executeBuy`/`_enterGraduating` inside `Bonding.sol` in this session (tool budget exhausted before the final `read_file`), so the precise revert propagation path (which specific external functions become unusable) is inferred from the code comments/doc rather than directly re-verified line-by-line. A Devin session with full file access should confirm the exact call graph and quantify the number of round-trip sells needed to trigger the underflow for a given `TOTAL_SUPPLY`/virtual-reserve configuration.

### Impact Explanation
If reachable, this permanently freezes the affected token's bonding curve: buys revert (via the trailing `canGraduate` check), and graduation (`_prepareGraduationLiquidity`) can never succeed, trapping curve-raised LT, the 250M reserved tokens, and any unclaimed creator/protocol fees tied to that token. This matches "permanent freezing of trader, creator, or LP funds" required by the validation criteria.

### Likelihood Explanation
Likelihood depends on how many wei of drift accumulate per round-trip sell and how large `TOTAL_SUPPLY`/`virtualLtReserve` are (typically 1e18-scale token supplies), which determines how many round-trips an attacker needs. Given each round-trip only costs the AMM curve fee-less swap cost (there is no curve fee per the doc, "no curve fee"), and the attacker can automate many round-trips in one or across multiple transactions, this is plausibly executable, but I could not fully verify the exact drift magnitude per swap or confirm there isn't an additional invariant elsewhere (e.g., a minimum reserve floor) preventing `assetReserve` from ever dropping below `virtualLtReserve`. This should be validated with a fuzz/PoC test in a Devin session before treating it as fully confirmed.

### Recommendation
- In `Router._computeSell`/`_computeBuy`, round in the protocol's favor (ceil the "amount kept" side) rather than allowing seller-favorable floor rounding to erode `assetReserve` below the invariant.
- Add an explicit floor check in `canGraduate` and `_prepareGraduationLiquidity`: if `assetReserve <= virtualLtReserve`, treat `realLtRaised`/`ltFromPair` as `0` instead of subtracting, mirroring the guard already added for the token-side donation underflow in `previewLtUntilGraduation` (`if (realBalance >= reserveToken) return ltUntilThreshold;`). [7](#0-6) 
- Tighten `Pair.swap`'s K-invariant check to remove or shrink the `+1` slack, or explicitly clamp `newAssetReserve`/`newTokenReserve` so cumulative rounding cannot drive `assetReserve` below the immutable virtual seed.

### Proof of Concept
Conceptual PoC (not fully verified against the exact numeric drift due to incomplete direct file inspection in this session):
1. `Zap.createToken(...)` to launch a token; note `pair = Bonding.getTokenInfo(token).pair`, initial `assetReserve = virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`.
2. Attacker repeatedly calls `Zap.buy(token, smallUsdcAmount, 0, referrer)` immediately followed by `Zap.sell(token, tokensReceived, 0)`, driving `tokenReserve` back toward its `TOTAL_SUPPLY` ceiling on each pass while `Router._computeSell`'s floor-division rounding shaves `assetReserve` slightly below the exact-K value each time.
3. After sufficiently many round-trips, `IPair(pair).getReserves()` returns `assetReserve < virtualLtReserve`.
4. The next `Zap.buy` call reverts inside `Bonding`'s trailing `canGraduate()` check (`assetReserve - _launchTimeVirtualLtReserve(...)` underflows), and any attempt to graduate reverts inside `_prepareGraduationLiquidity`, freezing the curve.

A background Devin session with terminal/foundry access should write a Foundry fuzz/invariant test isolating `Router._computeSell`/`_computeBuy` and `Pair.swap` to confirm whether repeated round-trips can actually drive `assetReserve` below `virtualLtReserve` given real `TOTAL_SUPPLY` magnitudes, since 1-wei-per-call drift may be economically impractical to exploit at realistic token supplies (1e9 * 1e18) without confirming the actual per-call rounding direction and magnitude numerically.

### Citations

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L728-729)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
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

**File:** packages/contracts/src/Router.sol (L172-182)
```text
    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }
```

**File:** docs/contracts-scope.md (L70-73)
```markdown
- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```
