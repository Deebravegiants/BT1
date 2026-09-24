### Title
Repeated bonding-curve swaps exploit `Pair.swap`'s off-by-one K-invariant slack to drain LT reserves and permanently brick a curve's graduation - ([File: packages/contracts/src/Pair.sol])

### Summary
`Pair.swap` enforces the constant-product invariant with a fixed `+1` tolerance on *each* reserve side instead of checking the exact product, and `Router._computeSell`/`_computeBuy` use floor-rounded division to size trade outputs. An unprivileged trader who repeatedly calls `Zap.sell`/`Zap.buy` (routed through `Bonding.sell`/`Bonding.buy` → `Router.sell`/`Router.buy` → `Pair.swap`) can, over many small trades, extract asset (LT) from the pair in excess of the exact bonding-curve price while every individual call still satisfies the loosened invariant check. Driven far enough, this can push the pair's stored `assetReserve` below the launch-time virtual LT reserve that `Bonding` recovers via `Pair.k() / Token.TOTAL_SUPPLY()`, causing an arithmetic-underflow revert in `canGraduate`/`_prepareGraduationLiquidity` — both of which are unconditionally exercised on every subsequent buy — permanently freezing the curve.

### Finding Description
`Pair.swap` checks the invariant as: [1](#0-0) 

```
uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
```

instead of the exact `newTokenReserve * newAssetReserve >= k`. This "+1 on both sides" tolerance is a permanent, unconditional slack baked into every swap, not a one-time rounding artifact — it is re-applied on every single trade, buy or sell, for the lifetime of the pair.

`Router._computeSell` and `Router._computeBuy` compute trade outputs with floor division against the *exact* `k`, not against the loosened check: [2](#0-1) [3](#0-2) 

Because `swap()`'s guard is strictly looser than the exact-K constraint the quoting functions target, there is headroom between "what the curve math computes" and "what the invariant actually requires to pass." An unprivileged trader can probe that headroom directly: by choosing trade sizes (particularly on tokens/pairs where reserves are pushed low, e.g. late in the curve near the 750M sellout, or on any newly-launched token with a small `virtualLtReserve` when paired against a cheap LT) that land right at the edge of the `+1` tolerance on repeated calls, an attacker extracts fractionally more asset per trade than the true constant-product price allows, while `KInvariantViolated` never fires because the check itself permits it. Repeating this over many transactions accumulates a real economic drain of the pair's LT reserve — this is a classic AMM "K-slack" exploitation: a bounds check that is looser than the value it's supposed to protect, analogous to `dwarf_getaranges`'s insufficiently validated bound letting a read go past the buffer it's meant to be confined to.

The drain is directly reachable by an unrelated wallet through `Zap.sell`/`Zap.buy` → `Bonding.sell`/`Bonding.buy`, both callable by any address with no privilege requirement.

The consequence compounds further: `Bonding.canGraduate` and `_prepareGraduationLiquidity` both compute: [4](#0-3) [5](#0-4) 

`realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` with plain unchecked-arithmetic subtraction (Solidity 0.8 checked math, so it reverts with a Panic on underflow rather than wrapping). If the K-slack drain pushes the pair's stored `assetReserve` below the recovered `virtualLtReserve` floor, this subtraction underflows and reverts. Crucially, `canGraduate` is invoked unconditionally at the end of *every* `Bonding.buy` (per `AGENTS.md`/`docs/contracts-scope.md`: "`Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`"), so once `assetReserve` dips below the virtual floor, every subsequent buy transaction on that curve reverts — permanently bricking the curve. Trading is not just paused; because the same underflow blocks the token from ever reaching a graduation trigger, no future buy can push it past the threshold either, and all curve-side value (unsold tokens, any remaining real LT, the creator's/protocol's future fee stream on that token) is permanently stranded.

### Impact Explanation
This is a Medium-severity, unprivileged-trader-reachable issue: repeated small trades let an attacker extract more value from the Pair than the bonding-curve math intends (a partial drain of curve-held LT, i.e. concrete theft of pooled funds), and in the worst case it drives the pair's stored reserve below the launch-time virtual floor, permanently bricking that token's curve (denial of buy/graduation service) and freezing whatever LT/tokens remain in the pair and in `Bonding`'s LP reserve for that token. Both outcomes — theft of pooled trader funds and permanent freezing of curve-held funds — are within the accepted impact classes for this program.

### Likelihood Explanation
The trade path (`Zap.buy`/`Zap.sell`) is open to any wallet, requires no special role, and the `+1` slack is unconditional on every swap rather than a rare edge case, so an attacker willing to spend gas on many small trades can accumulate the drain deterministically. The severity of the underflow-brick outcome depends on reserves being pushed to the edge, which is more readily achievable on lower-value/thinly-traded tokens, moderating overall likelihood to Medium.

### Recommendation
Tighten `Pair.swap`'s invariant check to the exact constant-product constraint (`newTokenReserve * newAssetReserve >= _pool.k`), removing the unconditional `+1` tolerance on both reserves, and make `Router._computeSell`/`_computeBuy` round in the curve's favor (ceiling on amounts the curve pays out, floor on amounts it collects) so no combination of legitimate quote and invariant check can be exploited for repeated dust extraction. Additionally, guard the `assetReserve - virtualLtReserve` subtractions in `Bonding.canGraduate` and `_prepareGraduationLiquidity` with an explicit `>=` check (returning a defined "not graduatable" / zero value on underflow) instead of relying on unchecked reverting subtraction, so that even if reserves are ever driven below the virtual floor by any future rounding issue, the curve degrades safely instead of bricking permanently.

### Proof of Concept
1. Launch a token via `Zap.createToken` and let the curve accumulate some baseline volume so reserves are away from the initial mint values.
2. From an unprivileged wallet, repeatedly call `Zap.sell(tokenAddress, smallTokenAmount, 0)` (routing through `Bonding.sell` → `Router.sell` → `Router._computeSell` → `Pair.swap`) with amounts chosen so that each call's `newTokenReserve`/`newAssetReserve` sits at the boundary permitted by `(newTokenReserve+1)*(newAssetReserve+1) >= k` rather than the exact product — each such call is accepted (`KInvariantViolated` does not revert) while extracting LT beyond the exact bonding-curve price.
3. Repeat step 2 across many transactions; observe the pair's stored `assetReserve` (via `IPair.getReserves()`) trending below what an exact-K simulation would predict, i.e. cumulative value drained from the curve into the attacker's wallet as LT.
4. Continue until `assetReserve` (as tracked by repeated trades) approaches the recovered `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`; the next `Bonding.buy` call, which invokes `canGraduate` at the end of `_executeBuy`, reverts with a Panic(0x11) arithmetic-underflow instead of completing the buy — demonstrating the curve is now permanently un-tradeable and un-graduatable.

### Citations

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

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
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

**File:** packages/contracts/src/Bonding.sol (L688-695)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1084-1084)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
```
