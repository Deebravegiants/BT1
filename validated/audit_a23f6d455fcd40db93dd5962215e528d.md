### Title
Dangling USDC allowance left on the leveraged-token contract after `Zap._executeBuy` mint - (File: `packages/contracts/src/Zap.sol`)

### Summary
`Zap._executeBuy` grants the reserve-asset leveraged token (`lt`) a `forceApprove` allowance over Zap's USDC before calling `lt.mint(...)`, but — unlike every other approval site in the same contract and in `Bonding.sol` — never zeroes that allowance afterward. This is the same bug class as CVE-2022-49463 (`imx_sc_thermal_probe` leaking a `of_node_put`-protected refcount on a code path that never releases what an earlier call acquired): a resource is acquired (`approve`) and the release step that every sibling code path performs is missing on this path, leaving a live, unbounded-until-overwritten grant to an external contract.

### Finding Description
In `_executeBuy` (`packages/contracts/src/Zap.sol:279-410`), both the post-graduation and pre-graduation mint branches do: [1](#0-0) [2](#0-1) 

`$.usdc.forceApprove(lt, baseToConvert)` sets Zap's USDC allowance to `lt` and the function returns without ever calling `$.usdc.forceApprove(lt, 0)`. Contrast this with the two other allowance-granting call sites in the same file and in `Bonding.sol`, both of which explicitly release the grant right after use: [3](#0-2) [4](#0-3) 

The `Bonding.sol` comment even documents the invariant this is supposed to uphold ("Approvals are reset to zero after `addLiquidity` returns... clearing it keeps the no-dangling-allowance invariant tidy"), but `Zap._executeBuy`'s two `mint()` approval sites are not held to that same invariant. `mint(address(this), baseToConvert, 0)` is a call into `lt`, an external, rebasing-priced BounceTech leveraged-token contract that Zap does not control and that the codebase's own `AGENTS.md` repeatedly treats as a source of drift/edge cases (exchange-rate drift, pausable minting, floor rounding). If `mint` ever pulls less than the full `baseToConvert` it was approved for — which is entirely plausible given the floor/rounding logic Zap itself works around a few lines above (`baseToConvert` is deliberately bumped/floored to satisfy BounceTech's own mint-floor arithmetic) — the unconsumed remainder of the allowance stays live on `lt` after the transaction ends, exactly analogous to a refcount that was incremented (`of_find_node_by_name`) and never decremented (`of_node_put`) on the return path.

### Impact Explanation
A standing non-zero USDC allowance held by the external `lt` contract over Zap means `lt` (or any code path inside it, including a future BounceTech operator action, an internal callback, or a bug in BounceTech's own contract) can call `transferFrom(Zap, ..., upToApprovedAmount)` on USDC at any later block, independent of and outside the original `buy` transaction. Since Zap continuously holds transient trader USDC/LT balances mid-flow (`_buyInternal`/`_sellInternal` route funds through Zap before forwarding), a dangling allowance is a live claim on protocol-adjacent funds sitting in Zap between transactions — this is a freezing/theft vector on trader funds that never should have been reachable once the `mint()` call returned. It also compounds: every subsequent `buy` calls `forceApprove(lt, baseToConvert)` again, so the residual is masked/overwritten by the next legitimate buyer's approval rather than being cleared, meaning the exposure window is continuously refreshed rather than closed.

### Likelihood Explanation
Reachable by any unprivileged trader simply by calling `Zap.buy` / `Zap.buyWithPermit` / `Zap.createToken` on the pre-graduation curve path or the post-graduation HyperSwap path — no special privileges required. The trigger condition (mint consuming less than the full approved amount) depends on BounceTech LT's exact `mint()` pull semantics, which Zap's own code (the floor-bump/rounding logic directly above the approval) shows are non-trivial and asymmetric versus what Zap computes locally; this uncertainty could not be fully resolved from the interface alone within the scope of this review, so the concrete magnitude of any un-consumed remainder is the part that would need runtime verification against the live BounceTech LT contract.

### Recommendation
Mirror the pattern already used at `Zap.sol:519` and `Bonding.sol:1471-1472`: call `$.usdc.forceApprove(lt, 0)` immediately after each `IBounceLeveragedToken(lt).mint(...)` call in `_executeBuy`, on both the graduated and pre-graduation branches, so no non-zero USDC allowance to `lt` survives past the buy transaction that created it.

### Proof of Concept
1. Trader calls `Zap.buy(tokenAddress, usdcAmount, 0, referrer)` on a curve-stage token.
2. Inside `_executeBuy`, Zap computes `baseToConvert` and calls `$.usdc.forceApprove(lt, baseToConvert)` followed by `IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0)`.
3. If `mint` pulls `< baseToConvert` USDC via `transferFrom` (e.g., due to any internal floor/rounding on BounceTech's side that does not match Zap's locally computed `baseToConvert`), the unspent allowance remainder (`baseToConvert - amountActuallyPulled`) is left approved to `lt` after the transaction completes — no code path in `_executeBuy` resets it.
4. `lt` (or any logic inside it) can subsequently call `transferFrom(zapAddress, x, remainder)` on USDC in a separate transaction, pulling funds out of Zap without a corresponding user-initiated `buy`. [5](#0-4)

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

**File:** packages/contracts/src/Zap.sol (L514-520)
```text
        IERC20(lt).forceApprove(address(curveRouter), ltAmount);
        // Slippage check happens after the refund path in `_buyInternal`.
        // `msg.sender` here is the user-EOA that called `Zap.buy`; passed
        // through as `trader` for the emitted `Trade` event.
        (tokensOut, amountInUsed) = bonding_.buy(ltAmount, tokenAddress, 0, msg.sender);
        IERC20(lt).forceApprove(address(curveRouter), 0);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1445-1472)
```text
    ///      Approvals are reset to zero after `addLiquidity` returns.
    ///      The router only pulls the matched-ratio subset, so unconsumed
    ///      desired amounts leave a residual allowance — clearing it
    ///      keeps the no-dangling-allowance invariant tidy.
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
            IERC20(lt).forceApprove(routerAddr, 0);
```
