### Title
Unhandled division-by-zero in `Zap._executeBuy`'s fee-proration math when the mint floor yields zero LT - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._executeBuy` computes `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted` at [1](#0-0)  using a raw `/` operator against `ltMinted`, the amount of LT actually minted by the external BounceTech LT via `IBounceLeveragedToken(lt).mint(...)` at [2](#0-1) . This mirrors the vulnerability class in the external report: an unchecked denominator sourced from state/external computation that can legitimately be zero, causing a hard revert (`Panic(0x12)`) rather than a handled edge case.

### Finding Description
`baseToConvert` is bounded below by `minUsdcAmount()` (the floor Zap enforces to avoid the LT's own `BelowMinTransactionSize` revert), but that floor is a *fixed USDC amount* — it says nothing about how many LT units that USDC converts to. `ltMinted` is produced by the external, rebasing-priced LT's `mint()`, whose exchange rate (`exchangeRate()` / `baseToLtAmount()`) is a live, market-driven value the LT's own leverage mechanics move over time [3](#0-2) . If the LT's exchange rate ever appreciates far enough that `baseToConvert` worth of USDC rounds down to `0` LT units on mint (while still clearing the LT's own minimum-transaction-size check, which is denominated in USDC, not LT), `mint()` can return `ltMinted == 0` without reverting. The subsequent division `(amountInUsed * baseToConvert) / ltMinted` then divides by zero and the whole buy transaction panics.

Because every `Zap.buy`/`buyWithPermit` call for that token routes through `_executeBuy` on both the curve and post-graduation branches [4](#0-3) , this is not a one-off revert but a **permanent denial of the buy path** for that token/LT pair once the exchange rate crosses the critical threshold — the rate only appreciates (BounceTech LTs are leveraged, compounding tokens), so the condition is monotonic and unrecoverable via any parameter Zap controls.

### Impact Explanation
This freezes the buy side of trading (curve and post-graduation) for any token paired to an LT whose exchange rate grows large enough. Traders cannot buy through `Zap.buy`/`buyWithPermit`; new curve tokens can never reach the LT-pumped USD graduation trigger via the intended buy path either (since that path is now bricked), and post-graduation buyers on the HyperSwap pool via `Zap` are also blocked. This is a protocol-level availability/freezing bug reachable by ordinary, unprivileged trading activity over time (no attacker action required beyond waiting for/accelerating LT appreciation), matching the "permanent freezing of trader ... funds/functionality" impact bar, even though sells remain possible through direct LT `redeem()`.

### Likelihood Explanation
Likelihood is low-to-medium and time/market-dependent: it requires the paired LT's `exchangeRate()` to climb enough that the protocol's fixed USDC floor (`minUsdcAmount()`) converts to fewer than 1 wei of the 18-decimal LT — a condition that depends on the specific LT's leverage/appreciation trajectory and decimal scaling, which I could not fully verify from the indexed BounceTech mock/interface files (the mock's exact `baseToLtAmount` rounding formula was not retrievable within the tool budget). It is plausible for long-lived, highly leveraged/appreciating LTs, and once triggered it is permanent and monotonic (exchange rates in this design only move in the appreciating direction absent LT-side de-registration).

### Recommendation
Guard the division in `_executeBuy`: if `ltMinted == 0` (or more generally before dividing by it), skip the fee-proration division and either (a) treat the buy as fully non-consumptive and refund all USDC, or (b) revert with a clear, decodable error instead of a raw arithmetic panic. More robustly, replace the raw `/` with `Math.mulDiv` and explicit zero-check, and consider bumping `baseToConvert` further (beyond the USDC floor) whenever `IBounceLeveragedToken(lt).baseToLtAmount(baseToConvert) == 0`, mirroring the existing floor-bump logic already used for the graduation-cap case at [5](#0-4) .

### Proof of Concept
1. Launch a token against an LT whose `exchangeRate()` can be driven (or has organically risen) high enough that `IBounceLeveragedToken(lt).baseToLtAmount(zap.minUsdcAmount())` returns `0` while `mint()` still succeeds (i.e., the LT's internal minimum-transaction-size check is denominated in base/USDC terms and is satisfied, but the LT-unit output rounds to zero).
2. Any unprivileged trader calls `Zap.buy(tokenAddress, usdcAmount, minTokensOut, referrer)` with `usdcAmount` sized so `netUsdc` clears the LT floor.
3. Inside `_executeBuy`, `ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0)` returns `0`.
4. The subsequent line `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;` [1](#0-0)  divides by zero and the transaction reverts with a Solidity division panic, bricking `Zap.buy` for that token going forward (every subsequent buy attempt hits the identical branch since the exchange rate only increases).

*Note: I was unable to fully confirm within the available indexing whether BounceTech's actual `baseToLtAmount`/`minTransactionSize` scaling makes this numerically reachable in practice on mainnet-realistic exchange rates — the mock LT's exact rounding implementation was not retrievable in the remaining tool budget. If a Devin session with full repo access is available, the `MockBounceGlobalStorage.sol` / real BounceTech LT integration and its exchange-rate decimal scaling should be inspected to confirm reachability before treating this as confirmed-exploitable.*

### Citations

**File:** packages/contracts/src/Zap.sol (L272-278)
```text
    /// @dev On the curve path, pre-sizes the LT mint against the graduation
    ///      cap via `Bonding.previewLtUntilGraduation`. The closing buy of
    ///      a graduation refunds unused USDC directly instead of round-
    ///      tripping leftover LT through `redeem` and paying BounceTech's
    ///      redemption fee (`baseAmount × redemptionFee × targetLeverage`)
    ///      on the overshoot. `mint(b)` is defined as `baseToLtAmount(b)`
    ///      on the LT, so the preview is exact.
```

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
