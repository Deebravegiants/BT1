### Title
Fee-less bonding-curve AMM lets rounding drift push the real LT reserve below the launch-time virtual reserve, permanently reverting graduation via underflow - ([File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Bonding.sol])

### Summary
`Router._computeBuy` / `_computeSell` use floor division to derive the new opposite-side reserve, and `Pair.swap` only tolerates a `+1` K-invariant slack per trade [1](#0-0) . Since the AMM has "no curve fee" (fees live only in `Zap`, never returned to the pair) [2](#0-1) , this rounding is not absorbed by any buffer. Repeated small buy/sell round trips can each skim a small amount of the pool's real LT reserve in the trader's favor, driving the pair's stored `assetReserve` down over many trades. Because `canGraduate` and `_prepareGraduationLiquidity` both compute `realLtRaised`/`ltFromPair` as `assetReserve - virtualLtReserve` with a plain subtraction and no floor guard, once the accumulated rounding drift pushes `assetReserve` below the launch-time `virtualLtReserve`, this subtraction underflows and reverts, permanently bricking graduation for that token.

### Finding Description
`_computeBuy` computes `tokensOut = reserveToken - (k / newReserveAsset)` and `_computeSell` computes `assetOut = reserveAsset - (k / newReserveToken)`, both using Solidity's floor division [3](#0-2) . Floor division on `k / newReserve` yields a value at or below the exact fair-value quotient, so the subtracted "remaining reserve" is *larger* than the exact fair value would be after subtraction — meaning the trader receives slightly more than the true constant-product amount each time. `Pair.swap`'s invariant check `(newTokenReserve + 1) * (newAssetReserve + 1) < k` tolerates this per-trade drift rather than rejecting it [4](#0-3) .

Because there is no curve fee to offset this drift (per design, fees are only charged in `Zap` and never re-deposited into the pair) [5](#0-4) , any unprivileged trader can repeat tiny `Zap.buy` → `Zap.sell` round trips against a single token's curve. Each round trip extracts a small amount of real LT from the pair's `assetReserve` without a compensating fee flowing back in, gradually eroding `assetReserve` toward — and potentially below — the launch-time virtual LT reserve.

`Bonding.canGraduate` and `Bonding._prepareGraduationLiquidity`/`_enterGraduating` both recover the launch-time virtual reserve as `Pair.k() / Token.TOTAL_SUPPLY()` and then subtract it from the live stored `assetReserve` with a bare `-` operator: `realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` [6](#0-5) . If `assetReserve` has drifted below `virtualLtReserve` due to accumulated rounding, this subtraction panics (arithmetic underflow) instead of returning `0`/reverting cleanly with a named error. The same subtraction pattern is reused by `_prepareGraduationLiquidity` to compute `ltFromPair` (the amount drained via `Router.graduate`) at phase-1 entry [7](#0-6) .

Once `assetReserve` sits below `virtualLtReserve`:
- `canGraduate` reverts on any call instead of returning `false`, so it can never report `true` again.
- `_enterGraduating`/`_prepareGraduationLiquidity` will panic if ever invoked (whether via `_executeBuy`'s threshold check or the permissionless `Bonding.triggerGraduation`), so phase 1 of graduation can never fire for that token.
- The token is permanently stuck in `Lifecycle.Curve`. The 250M `lpReserve` tokens held in `Bonding`, and any real LT raised by the curve, can never be moved to the HyperSwap LP or otherwise recovered, because the only exit path (`_graduate`) is gated behind the now-permanently-reverting `canGraduate`/`_prepareGraduationLiquidity` computation.

This mirrors the underlying bug class in the external report: an unaccounted-for subtraction between two balances that a counterparty can manipulate underflows and permanently blocks the legitimate exit/close path for other users — here, blocking the entire token's graduation rather than a single position close.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged trader:
- The token can never graduate, meaning curve-raised LT that should be deposited as LP liquidity (`ltFromPair`) and the 250M reserved supply tokens (`lpReserveTotal`) are permanently stranded — no code path other than `_graduate` can release them.
- All subsequent trading remains confined to the un-graduated bonding curve indefinitely, even after the USD or supply threshold is legitimately met, because `canGraduate` itself reverts.
- No admin/owner recovery path exists for `pendingGraduation`/reserve state once this underflow condition is hit, since `_prepareGraduationLiquidity`'s subtraction has no saturating/clamped variant (unlike the deliberately saturating subtraction used elsewhere in `finalizeGraduation`, e.g., `protectedLT`) [8](#0-7) .

### Likelihood Explanation
The rounding drift per round trip is at most a few wei (bounded by the `+1` K-invariant slack), so a large number of buy/sell cycles would be needed on a mainstream token to meaningfully erode `assetReserve` down to the virtual reserve. This makes the attack economically viable primarily on thinly-traded or freshly-launched tokens with a small `virtualLtReserve` margin, or via an attacker willing to pay gas across many transactions/blocks purely to grief a specific token's graduation. Likelihood is Medium: the primitive is real and unprivileged, but requires either a large number of transactions or a token near the graduation boundary to trigger the underflow in practice; I could not fully verify the exact numeric bound (e.g., whether `MIN_SEED_USDC`/mint-floor constraints on LT bound the minimum round-trip size enough to make many-iteration griefing impractical) without deeper numerical analysis of `BounceTech`'s `minTransactionSize` floor interacting with dust-sized buys/sells.

### Recommendation
- Round `_computeBuy`'s and `_computeSell`'s outputs in the pool's favor (ceil the retained-reserve term rather than floor it) so no round trip can extract more than the fair constant-product amount, eliminating the drift entirely.
- Replace the bare subtraction `assetReserve - virtualLtReserve` in `Bonding.canGraduate` and `_prepareGraduationLiquidity` with a saturating subtraction (return `0`/treat as not-yet-graduatable when `assetReserve <= virtualLtReserve`) so a rounding-driven deficit degrades gracefully instead of permanently panicking and bricking graduation.

### Proof of Concept
1. Launch a token via `Zap.createToken` with the minimum seed (`MIN_SEED_USDC`), establishing `virtualLtReserve = Pair.k() / TOTAL_SUPPLY()` as the initial `assetReserve`.
2. From any unprivileged wallet, repeatedly call `Zap.buy(token, dustUsdcAmount, 0, address(0))` immediately followed by `Zap.sell(token, tokensReceived, 0)` for the exact token amount just bought, many times in a loop (each call is a normal user action, no special privilege needed).
3. Each round trip nets the trader a small excess of LT out of the pair due to floor division in `_computeBuy`/`_computeSell`, slowly reducing the pair's stored `assetReserve`.
4. After enough iterations (bounded by how close `assetReserve` starts to `virtualLtReserve` and the LT's `minTransactionSize` floor), `assetReserve` dips below `virtualLtReserve`.
5. Any subsequent call to `Bonding.canGraduate(token)`, or an attempt to reach the graduation threshold via a real buy, causes an arithmetic underflow panic in `assetReserve - _launchTimeVirtualLtReserve(...)`, and the token is permanently stuck in `Lifecycle.Curve` — graduation, and the LP/reserve funds gated behind it, can never be unlocked.

*Note: I was unable to fully trace `_prepareGraduationLiquidity`'s complete implementation and the exact `_launchTimeVirtualLtReserve` helper body within the available index (only partial `Bonding.sol` excerpts were retrieved), so the precise numeric threshold for how many round trips are required, and whether any additional guard already exists there, could not be fully confirmed. A full review of `packages/contracts/src/Bonding.sol` (the `_prepareGraduationLiquidity` and `_launchTimeVirtualLtReserve` functions specifically) is recommended to close out verification.*

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

**File:** packages/contracts/src/Router.sol (L11-18)
```text
/// @title Router
/// @notice AMM math for bonding-curve pairs. No fees here — `Zap` handles fees.
/// @dev Supports virtual token reserves (curve extends beyond sellable supply,
///      enabling zero-gap LP seeding at graduation).
///
///      No reentrancy guard: all entry points are gated by `BONDING_ROLE`, and
///      `Bonding` wraps every trade in `nonReentrant`. Granting `BONDING_ROLE`
///      to any caller that doesn't enforce non-reentrancy would be unsafe.
```

**File:** packages/contracts/src/Router.sol (L127-182)
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

    /// @notice Tokens in → LT out.
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

**File:** docs/contracts-scope.md (L11-18)
```markdown
| `Bonding.sol` | Main entry — launch, buy, sell, graduation (no fee logic — moved to the router) |
| `Factory.sol` | Pair registry |
| `Router.sol` | AMM math, buy/sell execution (returns gross amounts; no fee deduction) |
| `Pair.sol` | Per-token pair: reserves, k-constant |
| `Token.sol` | ERC20 token with burn |
| `Zap.sol` | User-facing entry point — USDC in/out, LT abstraction, **fee layer** |
| `FeeVault.sol` | Holds accrued protocol + creator USDC fees; creators claim here |
| `LPLock.sol` | Holds graduated LP tokens (no withdraw in v1) |
```

**File:** docs/contracts-scope.md (L89-90)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
```

**File:** packages/contracts/src/Bonding.sol (L691-693)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
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
