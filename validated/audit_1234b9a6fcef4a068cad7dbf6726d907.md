## Title
Buyers can lose LT/USDC to the curve with zero tokens received on dust-sized buys — no zero-output guard in `Router._computeBuy`/`Bonding.buy` (File: `packages/contracts/src/Router.sol`, `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Zap.sol`)

### Summary
`Router._computeBuy` can return `tokensOut == 0` for small `amountIn` values due to integer-division rounding, yet the full `amountIn` is still consumed by the curve. Neither `Router.buy`, `Bonding.buy`, nor `Zap._buyInternal` reject a zero-token output, so a buyer whose transaction is not protected by a strictly-positive slippage floor pays real value (LT, and by extension USDC via `Zap`) and receives nothing in return — the exact "user loses funds on dust trade because output rounds to zero, with no zero-check" bug class from the referenced report, applied to alt.fun's constant-product curve instead of Notional's nToken redemption math.

### Finding Description
`Router._computeBuy` computes the curve output as: [1](#0-0) 

```
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);
```

For a sufficiently small `amountInUsed` relative to `reserveAsset`, `k / newReserveAsset` can round down to the same integer value as `k / reserveAsset` (or even round *up* by less than one whole token), making `tokensOut == 0`. There is no check anywhere in `_computeBuy` that `tokensOut > 0`.

`Router.buy` then unconditionally pulls the full `amountInUsed` LT from the caller into the pair and calls `transferToken(to, tokensOut)` / `swap(...)` with `tokensOut == 0`: [2](#0-1) 

`Bonding.buy` only guards against this via the caller-supplied `amountOutMin`: [3](#0-2) 

```
(tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
if (tokensOut < amountOutMin) revert SlippageExceeded();
```

If `amountOutMin == 0` (the default a caller would naturally pass for a "no slippage protection" or dust-size buy, and the value `Zap` itself passes through from `minTokensOut` with no protocol-enforced floor), `0 < 0` is false and the check does **not** revert.

Downstream, `Zap._buyInternal` (previously reviewed) unconditionally transfers `tokensOut` (possibly `0`) to the buyer, charges the buy fee, and only refunds any *LT* that the curve genuinely didn't consume (`ltExcess = ltMinted - amountInUsed`). On the non-capped path (the dust-buy scenario), `amountInUsed == ltMinted`, so `ltExcess == 0` — nothing is refunded even though the buyer received zero tokens: [4](#0-3) 

Unlike the sell path, which has a post-hoc `minUsdcAmount()` gate (`grossUsdcEstimate / 1e12 < minUsdcAmount()`) that reverts the whole atomic transaction if the trade nets to dust, the buy path has no equivalent minimum-output floor enforced by the protocol itself — the only backstop is a caller-supplied `minTokensOut`, which a buyer can (and by default might) set to `0`.

### Impact Explanation
A buyer submitting `Zap.buy(tokenAddress, usdcAmount, 0 /* minTokensOut */, referrer)` (or `Bonding.buy` directly through any allowlisted router with `amountOutMin = 0`) with a `usdcAmount` small enough that its LT-equivalent lands in the curve's rounding dead-zone pays the Alt Fun buy fee and has their LT fully consumed by `Router.swap`, but receives `0` tokens and no LT/USDC refund. This is a direct, permanent loss of user funds — the same class of bug as the referenced report (value consumed with zero output due to unchecked rounding-to-zero), just manifesting in the AMM buy leg instead of an nToken redemption calculation.

### Likelihood Explanation
Reachable by any unprivileged user via `Zap.buy`/`Zap.buyWithPermit` with ordinary parameters — no privileged role, no special preconditions beyond choosing (or defaulting to) `minTokensOut = 0` and a sufficiently small `usdcAmount`. The dust window's exact size depends on the pair's live reserves (`reserveAsset`, `k`), so it shrinks as the curve is bought up and is largest immediately after launch when `reserveAsset` (and thus `k`) is smallest, but the zero-output condition is a pure function of `Router._computeBuy`'s integer division and is always reachable for some sufficiently small `amountIn`.

### Recommendation
Add an explicit check in `Router._computeBuy` / `Router.buy` (or in `Bonding.buy`/`Bonding._executeBuy`) that reverts (e.g. `ZeroAmount`/a new `ZeroTokensOut` error) whenever `tokensOut == 0` for a nonzero `amountIn`, mirroring the zero-output revert that already exists on the sell side (`Zap._sellInternal`'s `BelowMinAmount` check). This ensures a buyer can never have their LT consumed for zero tokens regardless of the `minTokensOut` value they supply.

### Proof of Concept
1. Launch a token via `Zap.createToken(...)`, letting the curve seed with the standard virtual/real reserves (`reserve0 = totalSupply`, `reserve1 = virtual LT seed`, per `docs/contracts-scope.md`).
2. Immediately after launch (reserves still at their initial, largest `k`), compute a `usdcAmount` whose minted LT (`ltMinted`) satisfies `k / (reserveAsset + ltMinted) == k / reserveAsset` under integer division — i.e., an amount small enough that `tokensOut = reserveToken - (k / newReserveAsset)` rounds to `0` in `Router._computeBuy` (`packages/contracts/src/Router.sol:137-138`).
3. Call `Zap.buy(tokenAddress, usdcAmount, 0, address(0))` as an ordinary trader.
4. Observe: the Alt Fun buy fee is deducted, the minted LT is fully consumed as `amountInUsed` (non-capped path, so `ltExcess == 0`), `tokensOut == 0` is transferred to the trader, and `Bonding.buy`'s `tokensOut < amountOutMin` check (`0 < 0`) does not revert — the trader receives nothing for their spent USDC/LT.

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

**File:** packages/contracts/src/Bonding.sol (L563-580)
```text
    function buy(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256 tokensOut, uint256 amountInUsed) {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        // `creator == 0` means the slot was never written. `Lifecycle.Curve` is
        // the zero value, so without this an unknown token would fall through
        // and revert deep in `router.buy` with an opaque error.
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
    }
```

**File:** packages/contracts/src/Zap.sol (L361-410)
```text
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
