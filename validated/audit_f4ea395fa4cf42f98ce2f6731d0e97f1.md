### Title
`Zap._executeBuy` reverts with an unhandled division-by-zero when `ltMinted == 0`, DoS-ing buys once an LT's `exchangeRate()` grows large enough - (File: `packages/contracts/src/Zap.sol`)

### Summary
`BaseERC4626Proxy.exchangeRate()` reverts unconditionally when a denominator (`totalSupply()`) can legitimately be zero, breaking ERC-4626 compliance and DoS-ing dependent view/external functions. The analogous root cause exists in `Zap._executeBuy`: the fee-proration step divides by `ltMinted`, a value derived from the live, unbounded, externally-controlled `exchangeRate()` of the paired BounceTech LT, with no guard against it rounding to zero.

### Finding Description
In `_executeBuy` (`packages/contracts/src/Zap.sol`), after minting LT from the user's USDC, the function computes: [1](#0-0) [2](#0-1) 

`ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0)` where `baseToConvert` is floored at `minUsdcAmount()` (a fixed 6-dp USDC constant), and `mint` internally computes `ltAmount = baseToLtAmount(baseAmount) = baseAmount * 1e18 / exchangeRate()` [3](#0-2) . Because `exchangeRate()` is a live, externally-controlled, unbounded value (the LT's leveraged, rebasing USDC-per-LT price), if it grows large enough relative to the fixed USDC floor, `baseToLtAmount(baseToConvert)` — and therefore `ltMinted` — rounds down to `0`. The subsequent unconditional division `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;` then divides by zero and reverts, per Solidity 0.8's built-in overflow/division checks. This is functionally identical to `exchangeRate()`'s `.div(supply)` reverting on `supply == 0` in the report: both paths compute an intermediate quantity from a live, protocol-external variable and feed it into a denominator with no zero-guard, causing an "unexpected" revert instead of degrading gracefully.

Unlike `Bonding.previewLtUntilGraduation`, which explicitly guards its `exchangeRate`-derived division with `if (exchangeRate > 0)` [4](#0-3) , and `Bonding._deployAndSeed`, which reverts early with a named error if `exchangeRate == 0` [5](#0-4) , `Zap._executeBuy`'s `ltMinted` denominator has no equivalent guard.

### Impact Explanation
Once a paired LT's `exchangeRate()` rises far enough that `baseToLtAmount(minUsdcAmount())` rounds to `0`, **every** call to `Zap.buy` / `Zap.buyWithPermit` / `Zap.createToken` for that token reverts unconditionally — on both the bonding-curve path and the post-graduation HyperSwap path, since the vulnerable line is shared code executed after both branches. This is a permanent, unrecoverable DoS of the buy side for that token: holders can still sell (the sell path does not share this division), but new buys — including the creator's mandatory seed buy on `createToken` — become permanently impossible. Because LT `exchangeRate()` is monotonically influenced by external leverage/price dynamics and is explicitly documented in this codebase as capable of drifting significantly over a token's lifetime (see the "Retired LTs" and drift-acceptance notes in `Bonding.sol`), this is a reachable, not merely theoretical, state for long-lived or highly leveraged LTs.

### Likelihood Explanation
Reaching this requires only that a paired LT's `exchangeRate()` climb high enough that `minUsdcAmount() * 1e18 / exchangeRate() < 1`. `minUsdcAmount()` is a small, fixed floor (order of $10 in raw 6dp USDC), so for a leveraged token that appreciates substantially (a realistic outcome for the intentionally leveraged/long-tail asset class this protocol pairs against), this threshold is reachable without any privileged action — purely from organic price movement of the external LT, which nobody controls or can be forced to avoid.

### Recommendation
Guard the division in `_executeBuy` against `ltMinted == 0` (return/refund the USDC as an unfilled buy, or revert with a dedicated, decodable error such as `BelowMinAmount`) instead of letting Solidity's implicit division-by-zero panic surface. Alternatively (or additionally), assert `ltMinted > 0` immediately after the `mint` call, mirroring the explicit zero-checks already used elsewhere in the codebase (`ZeroExchangeRate` in `Bonding._deployAndSeed`, the `exchangeRate > 0` guard in `Bonding.previewLtUntilGraduation`).

### Proof of Concept
1. Launch a token against an LT (`Bonding.launch` via `Zap.createToken`).
2. Have the LT's `exchangeRate()` appreciate (via BounceTech leverage mechanics) until `minUsdcAmount() * 1e18 / exchangeRate() == 0` — i.e. the LT's USD price per unit exceeds `minUsdcAmount() * 1e18` (with `minUsdcAmount()` on the order of `10e6`, this requires `exchangeRate() > 10e6 * 1e18 = 1e25`, a large but not implausible rate for a long-lived, high-leverage token).
3. Call `Zap.buy(tokenAddress, usdcAmount, 0, address(0))` with any `usdcAmount >= minUsdcAmount()`.
4. Inside `_executeBuy`, `baseToConvert` is at most `netUsdc`, and `IBounceLeveragedToken(lt).mint(...)` returns `ltMinted = baseToConvert * 1e18 / exchangeRate() == 0`.
5. Execution reaches `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;` with `ltMinted == 0`, and the transaction reverts with a division-by-zero panic, unconditionally blocking all further buys for that token. [6](#0-5)

### Citations

**File:** packages/contracts/src/Zap.sol (L279-410)
```text
    function _executeBuy(
        address tokenAddress,
        uint256 usdcAmount
    ) internal returns (uint256 tokensOut, uint256 amountInUsed, uint256 actualFee) {
        ZapStorage storage $ = _s();
        address lt = $.bonding.ltOf(tokenAddress);

        // Fee is charged on EVERY buy — bonding curve AND post-graduation.
        // This is intentional. Lifting the fee post-grad would silently
        // halve protocol+creator revenue the moment a token graduates and is
        // the opposite of what we want. The `if (isGraduated) ...` branch
        // below selects the venue (HyperSwap V2 vs. internal AMM `Router.sol`),
        // not the fee policy.
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
        // The LT floor applies to the post-fee amount forwarded to `mint`, not
        // the gross input — `_buyInternal`'s pre-check on `usdcAmount` leaves a
        // ~5-cent dirty band (`[MIN, MIN / (1 − buyFeeBps/BPS_DENOM)]`) where
        // the gross passes but `mint` reverts with the undecodable
        // `0x05eb05ac` selector that the pre-check exists to suppress.
        if (netUsdc < minUsdcAmount()) revert BelowMinAmount();

        $.usdc.safeTransferFrom(msg.sender, address(this), usdcAmount);

        // BounceTech LTs are mint-pausable (but NOT redeem-pausable). When
        // the LT operator pauses minting, this call reverts, so every buy
        // through Zap — bonding curve and post-graduation alike — DoSes for
        // that token while sells keep working (sells go through `redeem`,
        // not `mint`). This is an accepted v1 tradeoff: a sell-only market
        // is preferable to freezing both sides, since holders can still
        // exit to USDC. Post-graduation, anyone holding LT directly can
        // also still buy by swapping on the HyperSwap TOKEN/LT pair,
        // bypassing Zap. We do not mirror BounceTech's pause flag in
        // `Zap` (it would couple our pausing surface to theirs and add
        // storage with no security gain).
        uint256 baseToConvert;
        uint256 ltMinted;
        if ($.bonding.isGraduated(tokenAddress)) {
            baseToConvert = netUsdc;
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
            tokensOut = _buyOnUniswapV2(tokenAddress, lt, ltMinted);
            amountInUsed = ltMinted;
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);

            if (ltUntilGraduation >= ltIfFull) {
                baseToConvert = netUsdc;
            } else {
                // `ltToBaseAmount` floors. Bump up so `mint(baseToConvert)`
                // yields ≥ `ltUntilGraduation` and the cap-binding buy
                // actually flips `canGraduate` true — otherwise the
                // closing buy can miss graduation by 1-2 wei of LT.
                if (ltUntilGraduation > 0) {
                    baseToConvert = IBounceLeveragedToken(lt).ltToBaseAmount(ltUntilGraduation);
                    if (IBounceLeveragedToken(lt).baseToLtAmount(baseToConvert) < ltUntilGraduation) {
                        baseToConvert += 1;
                    }
                }
                if (baseToConvert > netUsdc) baseToConvert = netUsdc;

                // Floor-bump: the cap-implied mint can fall below the LT
                // mint floor (BounceTech reverts with `BelowMinTransactionSize`,
                // selector `0x05eb05ac`), making the token un-graduatable
                // via any `Zap.buy`. Mint at the floor instead and refund
                // the LT overshoot to `msg.sender` after the curve buy
                // (see the LT-excess transfer below). Refund must be in
                // LT, not USDC — round-tripping the overshoot through
                // `redeem` would re-incur BounceTech's redemption fee on
                // dust, defeating the pre-sizing optimisation this branch
                // exists for.
                uint256 floor = minUsdcAmount();
                if (baseToConvert < floor) {
                    baseToConvert = floor;
                    if (baseToConvert > netUsdc) revert BelowMinAmount();
                }
            }

            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
            (tokensOut, amountInUsed) = _buyOnCurve(tokenAddress, lt, ltMinted);
        }

        IERC20(tokenAddress).safeTransfer(msg.sender, tokensOut);

        // Refund LT we minted but the curve didn't consume. In the
        // floor-bump branch with supply-tight this is the meaningful
        // overshoot; on the dust-cap branch it's at most sub-wei from
        // `_computeBuy`'s round-up; on the non-cap and post-graduation
        // branches it's identically zero (`amountInUsed == ltMinted` by
        // construction). Sent to `msg.sender` — `_buyInternal` is
        // `nonReentrant`, mirroring the safe-transfer-at-end-of-flow
        // pattern used for the USDC refund below.
        uint256 ltExcess = ltMinted - amountInUsed;
        if (ltExcess > 0) {
            IERC20(lt).safeTransfer(msg.sender, ltExcess);
        }

        // Pro-rate fees against the LT actually consumed by the curve.
        // For non-cap and dust-cap buys `amountInUsed ≈ ltMinted` so
        // `effectiveBaseSpent ≈ baseToConvert` and behaviour matches the
        // pre-floor-bump formula. The floor-bump branch overshoots the
        // mint past what the curve consumes; charging fee on the minted
        // size (rather than the consumed slice) would over-charge users
        // who hit this dust band.
        uint256 effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;
        // Round the prorated fee up in favour of the protocol and creator, then
        // cap it at the gross fee already withheld so the refund can't underflow
        // and a full-size buy never charges more than `feeOnGross`.
        actualFee = Math.mulDiv(usdcAmount * buyFeeBps_, effectiveBaseSpent, BPS_DENOM * netUsdc, Math.Rounding.Ceil);
        if (actualFee > feeOnGross) actualFee = feeOnGross;

        // `amountInUsed` (the curve-consumed LT) is not read by the caller, so
        // repurpose this return to report the USDC the trade actually spent on
        // the launched token: the curve-consumed slice plus the retained fee.
        // Using `effectiveBaseSpent` (not `baseToConvert`) excludes any LT
        // refunded to the buyer in the floor-bump branch, so the amount tracks
        // `tokensOut`. Equals the submitted amount on every non-capped buy.
        amountInUsed = effectiveBaseSpent + actualFee;

        uint256 feeRefund = feeOnGross - actualFee;

        uint256 usdcLeft = netUsdc - baseToConvert;
        if (usdcLeft > 0) {
            $.usdc.safeTransfer(msg.sender, usdcLeft);
        }
        if (feeRefund > 0) {
            $.usdc.safeTransfer(msg.sender, feeRefund);
        }
    }
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L31-35)
```text
    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);
```

**File:** packages/contracts/src/Bonding.sol (L477-479)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
```

**File:** packages/contracts/src/Bonding.sol (L720-726)
```text
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```
