Found the direct analog: `Router.buy` and `Router.sell` use the same "declared amount = credited amount" pattern flagged in the external report, applied to the LT reserve asset instead of an arbitrary ERC20.

### Title
Fee-on-transfer (or any balance-reducing) LT causes `Pair` reserve desync and permanent value leakage/DoS in `Router.buy`/`Router.sell` - ([File: packages/contracts/src/Router.sol])

### Summary
`Router.buy` and `Router.sell` credit the `Pair`'s stored reserves with the exact `amountInUsed`/`amountIn` value that was requested to be transferred via `safeTransferFrom`, without ever checking the `Pair`'s actual post-transfer balance. If the reserve asset (the LT wired at `Factory.ltFor(token)`/launch time) delivers less than the nominal amount on transfer, the stored reserve permanently overstates the real balance the `Pair` holds, exactly the pattern in the reported `DonationVotingMerkleDistributionVaultStrategy._afterAllocate` bug where `claims[...] += amount` used the nominal amount instead of a balance-before/after check.

### Finding Description
In `Router.buy` [1](#0-0) , `amountInUsed` LT is pulled from the trader straight into the `Pair` via `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`, and then `IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0)` unconditionally records `amountInUsed` as the asset-in leg of the reserve update — `Pair.swap` computes `newAssetReserve = pool.assetReserve + assetIn` purely from the passed-in `assetIn` argument, never reading `IERC20(assetToken).balanceOf(address(this))` [2](#0-1) . The same pattern exists in `Router.sell`'s token-in leg [3](#0-2) .

This differs from the canonical Uniswap V2 pattern (which reads `balanceOf` before/after a transfer to derive the real `amountIn`), and is exactly the root cause identified in the external report: an amount is "saved" (here, into `Pool.assetReserve`/`tokenReserve` via `k`-checked `swap`) using the nominal transferred amount rather than the balance actually received. `canGraduate`'s USD trigger and `previewLtUntilGraduation` both read these stored reserves directly (`assetReserve - virtualLtReserve`) [4](#0-3) , and `_prepareGraduationLiquidity`/`Router.graduate` later drains `ltFromPair = reserve1 - virtualLtReserve` LT out of the pair by calling `Pair.transferAsset`, which does a `safeTransfer` of that computed amount [5](#0-4) .

### Impact Explanation
If the wired LT ever delivers less than the requested `amountInUsed`/`assetOut` on a `transferFrom`/`transfer` (any balance-reducing behavior on transfer, not necessarily a classic percentage fee — e.g. a paused-transfer partial-refund path, a rebasing settlement quirk, or a future BounceTech LT variant with a transfer surcharge), the `Pair`'s stored `assetReserve` becomes permanently larger than its real LT balance. Consequences:
- The graduation USD trigger (`realLtRaised × exchangeRate`) is overstated, letting a token graduate on phantom LT it doesn't actually hold.
- `Router.graduate`'s `transferAsset(msg.sender, ltFromPair)` — using the inflated `ltFromPair` derived from the stored reserve — can attempt to move more LT out of the `Pair` than it actually holds, reverting `finalizeGraduation` (permanent DoS/brick of graduation for that token) or, if enough real LT sits in the pair from other trades, silently draining LT that should have stayed backing other traders' curve positions, i.e., insolvency/fund loss for later sellers who can no longer redeem the LT they're owed off the curve.
- Every subsequent `_computeBuy`/`_computeSell` quote (based on the now-wrong `k`/reserve state) misprices trades against the real balance, transferring value away from traders.

### Likelihood Explanation
Reachable by any unprivileged trader simply calling `Zap.buy`/`Zap.sell` (which route into `Router.buy`/`Router.sell`) once a bonding curve is live against an LT that exhibits any transfer-time value loss. The likelihood is contingent on the specific LT's transfer semantics — the currently reviewed `MockLeveragedToken`/BounceTech interface shows no fee-on-transfer today — so this is a latent design gap in `Router`/`Pair` rather than a proven exploit against the currently deployed LT, but the pattern is the exact analog the report describes and would activate immediately against any reserve asset that isn't balance-neutral on transfer.

### Recommendation
In `Pair.swap`/`Router.buy`/`Router.sell`, replace the caller-declared `amountInUsed`/`amountIn` credited into reserves with a balance-before/balance-after delta read via `IERC20(assetToken).balanceOf(address(this))` (and `IERC20(launchedToken).balanceOf(address(this))`), mirroring the standard Uniswap V2 `_update`/`skim`-style accounting, so the stored `Pool` reserves can never diverge from what the `Pair` actually holds regardless of the reserve asset's transfer behavior.

### Proof of Concept
1. Suppose the wired LT for a token is replaced/upgraded (or a new bonding curve is launched against an LT variant) that deducts 1% on `transferFrom` to a non-exempt address.
2. Trader calls `Zap.buy(token, usdcAmount, 0, ref)` → `Zap` mints `ltMinted` LT to itself → `_buyOnCurve` calls `bonding.buy(ltAmount, token, 0, trader)` → `Router.buy` computes `amountInUsed` and calls `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`.
3. The `Pair` actually receives `amountInUsed × 0.99` LT, but `IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0)` still credits the full `amountInUsed` into `_pool.assetReserve`.
4. `Pair.assetBalance()` (real `balanceOf`) is now permanently `1%` below `_pool.assetReserve` used by `canGraduate`/`previewLtUntilGraduation`/`_prepareGraduationLiquidity`.
5. At graduation, `Router.graduate(token, ltFromPair)` computes `ltFromPair` from the inflated stored reserve and calls `Pair.transferAsset`, which can revert (DoS) once the shortfall exceeds any real-balance slack, or succeed while draining LT that other curve participants are still owed.

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

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
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
