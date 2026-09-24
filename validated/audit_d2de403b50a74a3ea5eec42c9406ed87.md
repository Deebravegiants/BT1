### Title
`Zap.buy`/`createToken` seed path can consume a trader's USDC for zero output tokens without reverting - ([File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Zap.sol])

### Summary
The reported Perennial vault issue is that `_convertToShares` can round a deposit down to zero shares with no explicit check, silently taking the depositor's assets for nothing. The same structural gap — an AMM/conversion function that can legitimately return `0` output with no dedicated zero-output guard — exists on alt.fun's bonding-curve buy path. `Router._computeBuy` divides by the post-trade reserve (`k / newReserveAsset`) to derive `tokensOut`, and `Zap._executeBuy`/`_buyInternal` only guard against too-small output via the caller-supplied `minTokensOut`, not via an explicit `tokensOut > 0` check.

### Finding Description
`Router._computeBuy` computes the curve output purely from integer division: [1](#0-0) 

Nowhere in `Router.buy` or `_computeBuy` is there a check that `tokensOut != 0` — only `amountIn == 0` is rejected: [2](#0-1) 

On the `Zap` side, the only protection against a zero-value trade landing is the caller-supplied slippage floor: [3](#0-2) 

`if (tokensOut < minTokensOut) revert SlippageExceeded();` does **not** catch `tokensOut == 0` when `minTokensOut == 0`. This is precisely the scenario `Zap` itself deliberately creates for the mandatory launch seed buy: [4](#0-3) 

The comment explicitly says `minTokensOut = 0` is intentional "since there's nothing for slippage to protect against" — but this removes the only guard that could catch a rounding-to-zero trade. The same `minTokensOut = 0` pattern is available to any unprivileged trader calling `Zap.buy(tokenAddress, usdcAmount, 0, referrer)` directly.

Because `netUsdc` is only floored at a fixed USDC-denominated minimum (`minUsdcAmount()`, mirroring the LT's mint floor) rather than at a floor calibrated to the curve's live `reserveToken`/`reserveAsset` ratio, and because the reserve asset is an LT whose `exchangeRate()` is external and can move over time, the LT amount actually minted from a minimum-sized USDC buy can shrink to a point where `_computeBuy`'s `k / newReserveAsset` rounds `tokensOut` down to `0` (or the entire buy is otherwise absorbed by rounding), especially as `reserveAsset` grows large relative to `reserveToken` deep into the curve's life. Contrast this with the sell path, `_sellInternal`, which happens to catch a degenerate zero output indirectly via `grossUsdcEstimate / 1e12 < minUsdcAmount()` reverting the whole transaction — but no equivalent explicit check exists on the buy path once the trade has actually executed against the curve.

### Impact Explanation
A trader (or a token creator performing the mandatory seed buy in `Zap.createToken`) can have their full USDC principal pulled, converted to LT, and consumed by the curve (`amountInUsed == ltMinted` when no cap triggers) while receiving `0` launched tokens back, with `Zap._buyInternal` not reverting because `tokensOut < minTokensOut` is `0 < 0 == false`. This is a direct, unrecoverable loss of the trader's/creator's USDC — the exact impact class ("loss of assets for the depositor") called out in the source report — reachable from a plain `Zap.buy` call with no elevated privileges.

### Likelihood Explanation
Likelihood is elevated by three alt.fun-specific factors not present in a simple vault: (1) `minTokensOut = 0` is not just a user footgun but the codebase's own hardcoded choice for every `createToken` seed buy; (2) the reserve asset is a live, externally-priced LT whose `exchangeRate()` can drift the LT-denominated `netUsdc`→`baseToConvert` conversion arbitrarily, changing how close a minimum-sized buy sits to the rounding boundary over the life of a curve; (3) the fixed USDC floor (`minUsdcAmount()`) is not derived from, and does not track, the current `reserveToken`/`reserveAsset` ratio, so it provides no guarantee against `tokensOut` rounding to zero as the curve's `reserveAsset` grows toward the graduation threshold.

### Recommendation
Add an explicit `revert` in `Router._computeBuy`/`Router.buy` (or in `Zap._executeBuy` immediately after computing `tokensOut`) when `tokensOut == 0`, independent of the caller-supplied `minTokensOut`, mirroring the recommendation in the source report ("add a check to revert if zero shares/output are returned"). This closes the gap for both the general `Zap.buy` path and the hardcoded `minTokensOut = 0` seed-buy path in `Zap.createToken`.

### Proof of Concept
1. A token curve is deep enough into its life that `reserveAsset` (LT) is large relative to `reserveToken` (or the LT's `exchangeRate()` has moved such that a minimum-floor USDC buy converts to a very small LT amount).
2. Trader calls `Zap.buy(tokenAddress, minUsdcAmount(), 0, address(0))` — the minimum allowed buy size, with `minTokensOut = 0` (as the UI/creator seed path does by default).
3. `_executeBuy` mints LT for the full `netUsdc`, calls `_buyOnCurve` → `Router.buy` → `_computeBuy`, where `reserveToken - (k / newReserveAsset)` rounds down to `0`.
4. `amountInUsed == ltMinted` (no cap path triggered), so `ltExcess == 0` — no LT refund.
5. Back in `_buyInternal`, `tokensOut (0) < minTokensOut (0)` is `false`, so no `SlippageExceeded` revert; the trader's full USDC (minus/including fee) is consumed and `Buy` is emitted with `tokensOut = 0`.

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

**File:** packages/contracts/src/Zap.sol (L218-237)
```text
    function _createTokenInternal(
        Bonding.LaunchParams calldata params,
        uint256 seedUsdcAmount
    ) internal returns (address tokenAddr) {
        if (params.ltAddress == address(0)) revert InvalidInput();
        // Mandatory seed buy. See `MIN_SEED_USDC` for the no-cap rationale.
        // Floored at the live mint floor too, so a seed can't pass here and
        // then revert when it's minted (see `minSeedUsdc`).
        if (seedUsdcAmount < minSeedUsdc()) revert BelowMinSeed();

        (tokenAddr,) = _s().bonding.launch(params, msg.sender);
        emit TokenCreated(tokenAddr, msg.sender, params.ltAddress);

        // The seed buy is what arms the bypass into `Bonding`'s launch
        // trading delay — it MUST happen in the same tx as `bonding.launch`,
        // otherwise the transient flag clears and the buy reverts with
        // `TradingNotOpen`. `minTokensOut = 0` is intentional: same-tx as
        // launch, so there's nothing for slippage to protect against.
        _buyInternal(tokenAddr, seedUsdcAmount, 0, address(0));
    }
```

**File:** packages/contracts/src/Zap.sol (L252-270)
```text
        uint256 grossSpent;
        uint256 actualFee;
        (tokensOut, grossSpent, actualFee) = _executeBuy(tokenAddress, usdcAmount);

        if (tokensOut < minTokensOut) revert SlippageExceeded();

        if (actualFee > 0) {
            _accrueFee(tokenAddress, bonding_.creatorOf(tokenAddress), actualFee, true);
        }

        // Report the USDC actually spent, not the submitted `usdcAmount`. A
        // graduation-capped buy refunds the unused principal and fee, so the
        // two diverge there; for every other buy they're equal.
        emit Buy(tokenAddress, msg.sender, grossSpent, tokensOut);

        if (referrer != address(0) && referrer != msg.sender) {
            emit Referred(tokenAddress, msg.sender, referrer, grossSpent);
        }
    }
```
