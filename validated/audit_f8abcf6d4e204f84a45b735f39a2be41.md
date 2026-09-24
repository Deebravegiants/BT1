### Title
Unvalidated `assetReserve - virtualLtReserve` subtraction can Panic-revert and permanently freeze curve trading/graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes `llsec_do_decrypt_auth()` computing `assoclen += datalen - authlen` without first checking that `datalen >= authlen`, letting a short frame underflow the subtraction into a huge unsigned value. alt.fun's `Bonding.sol` contains the same *unguarded-subtraction* shape in the graduation math: `assetReserve - _launchTimeVirtualLtReserve(...)` is computed in three places — `canGraduate` [1](#0-0) , `previewLtUntilGraduation` [2](#0-1) , and `_prepareGraduationLiquidity` [3](#0-2)  — with **no check** that `assetReserve >= virtualLtReserve` before subtracting.

### Finding Description
`_launchTimeVirtualLtReserve` recovers the pair's launch-time virtual LT reserve as `Pair.k() / Token.TOTAL_SUPPLY()` [4](#0-3) . `canGraduate` then computes the "real LT raised" as:

```solidity
(, uint256 assetReserve) = IPair(pair).getReserves();
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
``` [1](#0-0) 

Solidity 0.8's checked arithmetic turns an underflow into a `Panic(0x11)` revert rather than a silent wraparound, but the effect is structurally identical to the CVE's root cause: a subtraction is performed on attacker-influenceable state without first validating that the minuend is at least as large as the subtrahend.

Critically, the developers were *already aware* of this exact underflow risk: `finalizeGraduation` applies a defensive **saturating** subtract on the analogous `ltBalance - p.ltFromPair` computation, with an explicit comment: *"a balance below `p.ltFromPair` shouldn't be reachable in normal operation, but we keep finalize from bricking on a Panic if any future code path... briefly violates the invariant"* [5](#0-4) . The identically-shaped `assetReserve - virtualLtReserve` subtraction in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` received no such guard.

`canGraduate` is not a peripheral view — it is invoked on **every single buy** via `_executeBuy` [6](#0-5)  and is used as a mandatory guard on **every sell** [7](#0-6) , and again inside `Zap._sellInternal` [8](#0-7) . If `assetReserve` ever dips even 1 wei below the recovered `virtualLtReserve`, every future buy and sell on that token's curve reverts with an unhandled Panic, permanently bricking the token.

The mechanism by which `assetReserve` could drop below `virtualLtReserve` is the same class of tolerance the report explicitly calls out as alt.fun's own attack surface: `Pair.swap`'s "`+1` K slack" — the invariant check accepts any post-swap state satisfying `(newTokenReserve+1)*(newAssetReserve+1) >= k`, i.e., up to `~(newTokenReserve+newAssetReserve)` less than the exact `k` product [9](#0-8) . `Router._computeSell`'s floor-rounded `assetOut` is designed to round in the curve's favor on any single call, but I was not able to fully verify — within the available tool budget — whether repeated buy/sell cycles that individually stay within the `+1` slack tolerance can, in aggregate, drift `assetReserve` below `virtualLtReserve`, nor could I construct/simulate a concrete numeric sequence proving the underflow is reachable from a single unprivileged trader's buy/sell calls alone.

### Impact Explanation
If reachable, this permanently freezes the affected token's curve: no further `Zap.buy`/`Zap.sell` (and therefore no `Bonding.buy`/`sell`/`triggerGraduation`) can succeed, since `canGraduate` (called on the hot path of every trade) reverts with an unhandled Panic. Traders' LT/tokens already committed to that curve become stuck pre-graduation with no exit path, matching the "permanent freezing of trader... funds" impact criterion.

### Likelihood Explanation
Medium-to-low confidence: the underflow requires `assetReserve` to fall strictly below the recovered `virtualLtReserve`, which the buy/sell rounding directions are designed to prevent on any individual trade. The developers' own asymmetric defensive coding (saturating-subtract in `finalizeGraduation` but not in `canGraduate`/`previewLtUntilGraduation`/`_prepareGraduationLiquidity`) is the strongest signal that this exact underflow was considered a real, if rare, risk by the team itself — but I could not confirm within this investigation whether the `+1` K-slack tolerance in `Pair.swap` is sufficient, over some sequence of legitimate curve trades, to actually drive `assetReserve` below `virtualLtReserve`.

### Recommendation
Apply the same saturating-subtraction (or an explicit `require(assetReserve >= virtualLtReserve)` pre-check with a defined fallback) used in `finalizeGraduation` to the identical computation in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity`, so a rounding-drift edge case degrades gracefully (e.g., treats `realLtRaised`/`ltFromPair` as `0`) instead of Panic-reverting and permanently freezing the curve.

### Proof of Concept
Not established. A concrete PoC would require enumerating a sequence of `Bonding.buy`/`Bonding.sell` calls (via `Zap.buy`/`Zap.sell`) that exploits the `Pair.swap` `+1` K-slack tolerance across repeated round trips to push the pair's stored `assetReserve` below `_launchTimeVirtualLtReserve`. I was unable to complete this numeric simulation within the available investigation budget; a Devin session with full repo/test access (e.g., extending `packages/contracts/test/GraduationInvariants.t.sol`) would be needed to confirm or refute reachability before treating this as a proven, exploitable finding.

### Citations

**File:** packages/contracts/src/Bonding.sol (L598-598)
```text
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();
```

**File:** packages/contracts/src/Bonding.sol (L691-693)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
```

**File:** packages/contracts/src/Bonding.sol (L722-722)
```text
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
```

**File:** packages/contracts/src/Bonding.sol (L929-931)
```text
        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1015-1020)
```text
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1084)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
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

**File:** packages/contracts/src/Zap.sol (L430-432)
```text
        if (bonding_.canGraduate(tokenAddress)) {
            if (minUsdcOut != 0) revert TokenIsGraduating();
            bonding_.triggerGraduation(tokenAddress);
```

**File:** packages/contracts/src/Pair.sol (L70-79)
```text
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
