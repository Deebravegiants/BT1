### Title
Accumulated `+1` K-slack rounding in `Pair.swap` can push `assetReserve` below the recovered launch-time virtual reserve, permanently bricking a token's curve via arithmetic underflow — ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.canGraduate`, `Bonding.previewLtUntilGraduation`, and `Bonding._prepareGraduationLiquidity` all compute `realLtRaised`/`ltFromPair` as `assetReserve - _launchTimeVirtualLtReserve(token_, pair)`, an unchecked subtraction that assumes `assetReserve` can never fall below the immutable virtual reserve recovered from `Pair.k() / Token.TOTAL_SUPPLY()`. `Pair.swap`'s invariant check, however, only enforces `(newTokenReserve+1)*(newAssetReserve+1) >= k`, a deliberate one-wei-per-side rounding slack (explicitly documented as the "+1 K slack"). Because this slack is applied on every trade, a sequence of ordinary buys/sells that drives `tokenReserve` back up toward its initial value `totalSupply` can leave `assetReserve` exactly one wei below the recovered `virtualLtReserve`. Any subsequent call that performs `assetReserve - virtualLtReserve` then reverts with an arithmetic-underflow Panic instead of returning a value. [1](#0-0) [2](#0-1) 

### Finding Description
`Pair.swap` updates reserves with plain integer addition/subtraction, and only gates the update behind a K-invariant check with a 1-unit slack on each side of the product: [2](#0-1) 

That `+1`/`+1` slack is the entire tolerance the AMM allows for integer-division rounding on `_computeBuy`/`_computeSell`. It is applied independently on every single trade, so successive buys and sells (a buyer opens tokens off the curve, then partially or fully sells them back) each get to "consume" up to one wei of rounding slack in the trader's favor. Because the slack is not bounded in aggregate across a token's lifetime, a long enough sequence of trades that returns `tokenReserve` close to its initial ceiling (`totalSupply`, the virtual token reserve baked in at `Pair.mint`) can leave the *stored* `assetReserve` strictly below the token's immutable virtual LT reserve, `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`.

`Bonding` recovers that virtual reserve via `_launchTimeVirtualLtReserve` and treats `assetReserve - virtualLtReserve` as a value that is always `>= 0`, in three places that are all on the hot buy/sell/graduation path: [3](#0-2) [4](#0-3) [5](#0-4) 

`canGraduate` is not a side path — it is called unconditionally on **every** curve buy (via `_executeBuy`) and **every** curve sell (as a pre-check), and also by the permissionless `triggerGraduation`: [6](#0-5) [7](#0-6) [8](#0-7) 

Once `assetReserve` dips one wei below the recovered `virtualLtReserve` for a given token, `canGraduate(token)` reverts with a Panic (arithmetic underflow) on its very first line of real logic. Since `buy`, `sell`, and `triggerGraduation` all call `canGraduate` (directly or via `_executeBuy`), the token becomes permanently untradeable and un-graduatable: every subsequent `Zap.buy`/`Zap.sell` for that token reverts, and it can never reach `finalizeGraduation`. This mirrors the CVE's root cause class — an off-by-one/boundary condition in a bounds/limit check that is only validated for the "normal" range and silently mis-behaves at the edge, producing an out-of-bounds-style failure (here, an underflow instead of a memory over-read) triggered purely by ordinary, permissionless input (a specific short/edge-case trade sequence, analogous to the CVE's "seven characters or fewer" boundary trigger).

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by unprivileged traders:
- Any real LT and unsold tokens already raised by the curve become permanently stuck in `Pair`/`Bonding` — no `sell` can execute (reverts before completing), no `buy` can execute, and `triggerGraduation`/the inline graduation trigger can never fire because `canGraduate` itself reverts.
- Every holder of the affected token's curve position, plus the creator's fee stream (no more trades → no more fees to `FeeVault`), is frozen indefinitely for that specific token.
- No admin recovery path exists: `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` are the only entry points into `Lifecycle.Graduating`/`Graduated`, and all three underflow identically since they use the same `assetReserve - virtualLtReserve` expression.

This satisfies "permanent freezing of trader, creator or LP funds" under the Validate criteria.

### Likelihood Explanation
Reachability requires only ordinary permissionless calls (`Zap.buy` / `Zap.sell`, or direct `Bonding.buy`/`sell` through an allowlisted router), no privileged role, and no external protocol bug — it is purely a consequence of alt.fun's own `Pair.swap` rounding slack combined with `Bonding`'s unchecked subtraction. The exact number and sizing of trades needed to accumulate a full wei of drift against `virtualLtReserve` (which can be in the thousands-of-ether range depending on the LT's `exchangeRate()`) was not something I could fully quantify from the code alone — confirming a concrete, minimal-cost trade sequence that reliably lands `assetReserve` exactly one wei short would require a fuzzing/PoC pass (e.g. in `Bonding.t.sol`/`Router.t.sol`) that is out of scope for this static review. I flag this as the main open uncertainty: the bug is provably possible given the "+1" slack design and the missing floor in `Bonding`, but I have not derived a guaranteed-successful concrete trade script here.

### Recommendation
- In `Bonding._launchTimeVirtualLtReserve`-consuming call sites (`canGraduate`, `previewLtUntilGraduation`, `_prepareGraduationLiquidity`), replace the raw subtraction with a saturating subtraction (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`), matching the defensive pattern already used elsewhere in the same file (e.g. `finalizeGraduation`'s `ltBalance > p.ltFromPair ? ... : 0`).
- Alternatively/additionally, tighten `Pair.swap`'s invariant check so the `+1` slack cannot be exploited cumulatively to drive `assetReserve` below the pair's immutable virtual floor, e.g. by asserting `newAssetReserve + 1 >= virtualLtReserve` (or the equivalent token-side floor) in addition to the aggregate K check.

### Proof of Concept
Conceptual PoC (requires simulation/fuzzing to nail exact amounts, not fully derived here):
1. Launch a token normally (`Zap.createToken`), establishing `Pair.k = TOTAL_SUPPLY * virtualLtReserve` and `tokenReserve = TOTAL_SUPPLY`, `assetReserve = virtualLtReserve`.
2. Have a trader `buy` a meaningful chunk of the curve, then `sell` it back, repeating buy/sell cycles that each land near the K-invariant's `+1` slack boundary (i.e., trade sizes chosen so `_computeBuy`/`_computeSell`'s rounding is favorable to the trader every time).
3. After enough cycles, `tokenReserve` returns close to `TOTAL_SUPPLY` while `assetReserve` has drifted to `virtualLtReserve - 1`.
4. Call `Bonding.canGraduate(token)` (or simply call `Zap.buy`/`Zap.sell` again, which invoke it internally) — this reverts with an arithmetic-underflow Panic (`0x11`), and the token's curve is now permanently un-tradeable and un-graduatable.

### Citations

**File:** packages/contracts/src/Bonding.sol (L583-606)
```text
    function sell(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();

        (, uint256 assetOut) = $.router.sell(amountIn, tokenAddress, msg.sender);
        if (assetOut < amountOutMin) revert SlippageExceeded();

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, false, assetOut, amountIn, newCurveSupply, newLtReserve);
        return assetOut;
    }
```

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L705-736)
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

        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
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

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
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
