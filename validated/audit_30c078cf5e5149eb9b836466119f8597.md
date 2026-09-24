### Title
Curve `Pair.swap` trusts Router-declared swap deltas instead of verifying real token/LT balance movement — ([File: packages/contracts/src/Pair.sol])

### Summary
`Pair.swap` updates its internal `tokenReserve`/`assetReserve` accounting purely from the `tokenIn/tokenOut/assetIn/assetOut` arguments `Router` passes in, and enforces the K-invariant against those *declared* deltas — never against the pair's actual measured `IERC20.balanceOf` before/after the transfers that just occurred. This is the same trust pattern as the Hono bug: a size/quantity check is satisfied against a caller-declared number instead of the value that was actually delivered on-chain.

### Finding Description
`Router.buy` and `Router.sell` compute `amountInUsed`/`tokensOut`/`assetOut` from the pair's *stored* reserves via `_computeBuy`/`_computeSell`, move tokens with `safeTransferFrom`/`transferToken`/`transferAsset`, and then call `Pair.swap` with those same computed numbers: [1](#0-0) [2](#0-1) 

`Pair.swap` itself never re-derives the deltas from real balances — it simply trusts the numbers `Router` hands it and checks K against them: [3](#0-2) 

This differs from genuine UniswapV2, where `swap()` reads `balance0`/`balance1` *after* the transfer and derives the real `amountIn` from the balance delta before checking K — the design that makes UniswapV2 resistant to any token whose delivered amount can diverge from the nominal transfer amount. Here, `_pool.assetReserve` is a pure bookkeeping number driven by `Router`'s declared `amountInUsed`/`assetOut`, decoupled from `Pair.assetBalance()` (`IERC20(assetToken).balanceOf(address(this))`), for the entire lifetime of the curve.

The `assetToken` side of every pair is a BounceTech Leveraged Token (LT) — an externally supplied, permissionlessly chosen contract at `launch()` time (only checked for registry membership via `IBounceFactory.ltExists`, not for transfer-safety): [4](#0-3) 

Because the LT is documented throughout the codebase as a rebasing-priced asset whose accounting (exchange rate, streaming fee, redemption fee) is settled at mint/redeem/transfer checkpoints rather than being a static-balance ERC20, any divergence between the LT amount `Router` *declares* it moved (`amountInUsed`, `assetOut`) and the LT amount the pair *actually* ends up holding is never detected or reconciled by `Pair`/`Router`. `Bonding.canGraduate` then reads the same unreconciled stored `assetReserve` to decide the USD graduation trigger, and `_prepareGraduationLiquidity`/`Router.graduate` later pulls real LT out of the pair based on that stored figure: [5](#0-4) [6](#0-5) 

If the recorded `assetReserve` ever runs ahead of the real `assetBalance()` — exactly the same "declared vs. delivered" gap the Hono advisory describes for `Content-Length` — a graduation can trigger on phantom reserve, and phase-2 seeding/`Router.graduate` can attempt to move out real LT the pair does not actually hold, either reverting the graduation (freezing curve-raised funds and the 250M reserved tokens escrowed on `Bonding` between phases) or, if the pair later receives unrelated top-up LT, paying out against another trader's principal.

### Impact Explanation
A permanent desync between `Pair`'s internal `assetReserve` bookkeeping and its real LT balance either bricks a token's graduation (curve-raised LT and the escrowed 250M tokens are permanently stuck in `Lifecycle.Graduating` with no way for `finalizeGraduation` to complete against a real balance that is short) or misallocates real LT belonging to later depositors when the shortfall is unknowingly backfilled — both are permanent freezing/misallocation of trader and creator funds, consistent with a Medium-severity finding.

### Likelihood Explanation
Every buy/sell on every curve token routes through this exact code path (`Zap.buy`/`Zap.sell` → `Bonding.buy`/`sell` → `Router.buy`/`sell` → `Pair.swap`), so the vulnerable machinery is on the hot path for all unprivileged traders. The trigger condition (declared swap delta ≠ real balance delta for the `assetToken`) depends on the specific BounceTech LT's transfer/settlement semantics, which alt.fun does not control and only network-registry-checks (`ltExists`), not balance-safety-checks, at launch — making likelihood credible but not proven against any specific already-deployed LT, since `Pair`/`Router` never instrument the divergence to confirm it in practice.

### Recommendation
Have `Router.buy`/`Router.sell` read `IPair.tokenBalance()`/`IPair.assetBalance()` immediately before and after each transfer and pass the *measured* deltas — not the pre-computed AMM-math deltas — into `Pair.swap`, mirroring UniswapV2's balance-diff pattern. Alternatively, have `Pair.swap` itself snapshot `assetBalance()`/`tokenBalance()` at entry and re-derive `assetIn`/`tokenOut` from the actual balance change rather than trusting `Router`'s arguments, so the K-check and all downstream graduation/LP-seeding logic operate on ground truth instead of a declared value that can drift from what was actually delivered.

### Proof of Concept
Conceptual sequence (cannot be fully proven without BounceTech LT transfer-settlement source, which is out of scope):
1. Token creator launches a token pairing it with an LT whose `transferFrom`/`transfer` settlement delivers less than the nominal amount to the recipient (e.g., a streaming-fee checkpoint realized as a balance adjustment on transfer).
2. A trader calls `Zap.buy` → `Bonding.buy` → `Router.buy`, which computes `amountInUsed` from stored reserves and calls `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`, then unconditionally reports `assetIn = amountInUsed` to `Pair.swap` [7](#0-6) .
3. `Pair._pool.assetReserve` increases by the full declared `amountInUsed`, while `Pair.assetBalance()` (real `balanceOf`) increases by less.
4. Repeated trades widen the gap; `Bonding.canGraduate`'s USD leg computed off the inflated stored `assetReserve` [8](#0-7)  can trip early, and `Router.graduate`'s `transferAsset(msg.sender, amount)` [6](#0-5)  then attempts to move more real LT out of the pair than it actually holds, reverting `finalizeGraduation` and permanently stranding the curve-raised LT and escrowed 250M tokens on `Bonding`.

### Citations

**File:** packages/contracts/src/Router.sol (L92-108)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }
```

**File:** packages/contracts/src/Router.sol (L151-170)
```text
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }
```

**File:** packages/contracts/src/Router.sol (L203-211)
```text
    function graduate(
        address token,
        uint256 amount
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        IPair(pairAddr).transferAsset(msg.sender, amount);
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

**File:** packages/contracts/src/Bonding.sol (L396-400)
```text
        // `Zap.createToken` is permissionless; without this gate a fake LT
        // could siphon USDC inside `mint` (which `Zap` `forceApprove`s).
        if (!IBounceFactory($.bounceGlobalStorage.factory()).ltExists(params.ltAddress)) {
            revert UnknownLeveragedToken(params.ltAddress);
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
