### Title
Router trusts nominal transfer amounts instead of measured pair-balance deltas when crediting the K-invariant swap - ([File: packages/contracts/src/Router.sol])

### Summary
`Router.buy` and `Router.sell` call `safeTransferFrom`/rely on the caller having transferred an exact nominal amount into the `Pair`, then feed that same nominal amount straight into `Pair.swap()`'s reserve bookkeeping and K-invariant check — never re-reading `Pair.tokenBalance()`/`Pair.assetBalance()` before/after the transfer to confirm the pair actually received that amount. This is the same root-cause class as the reported `_safeRewardTransfer` finding: trusting a stated transfer amount rather than verifying the actual balance delta, which is unsafe whenever the transferred asset's `balanceOf` accounting can diverge from the nominal amount moved.

### Finding Description
In `Router.buy`: [1](#0-0) 
the router computes `amountInUsed` purely from stored reserves via `_computeBuy`, then does:
```
IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);
IPair(pairAddr).transferToken(to, tokensOut);
IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
```
`Pair.swap` then updates `_pool.assetReserve` by adding the passed-in `assetIn` (`amountInUsed`) and checks the K-invariant against that same nominal figure — it never reads `IERC20(assetToken).balanceOf(pairAddr)` to confirm the pair's real balance moved by `amountInUsed`: [2](#0-1) 

`Router.sell` has the identical structure on the token leg — `safeTransferFrom(to, pairAddr, amountIn)` followed by `swap(amountIn, 0, 0, assetOut)` using the nominal `amountIn`, with no balance-delta check: [3](#0-2) 

The reserve asset (`assetToken`) is the external BounceTech Leveraged Token (LT), integrated purely through its declared interface (`mint`/`redeem`/`exchangeRate`) with no independent verification that its `transferFrom` moves exactly the requested amount into `balanceOf`: [4](#0-3) 
Nothing in `Router`, `Pair`, or `Bonding` cross-checks `pair.assetBalance()`/`pair.tokenBalance()` against the nominal `amountInUsed`/`amountIn` before committing the swap's reserve update. If the reserve asset's `transferFrom` ever delivers less (or more) than the requested amount — e.g. a future BounceTech upgrade adding a transfer fee, a pausable/partial-transfer path, or any other divergence between "amount requested" and "amount received" — the pair's internal `_pool.assetReserve`/`tokenReserve` accounting permanently diverges from the pair's real token balances. Because `Pair.swap`'s K-check is computed purely off the stored `_pool` state (never against live `balanceOf`), this divergence is not caught at the point of injection; it silently corrupts the AMM's pricing curve and the graduation math that later reads `getReserves()`/`k()` to compute `ltFromPair`/`tokensForLP`.

### Impact Explanation
If the reserve-asset transfer amount and the actual balance delta diverge, the bonding curve's stored reserves become permanently desynchronized from real balances:
- Every subsequent buy/sell is mispriced off the corrupted `_pool.assetReserve`/`tokenReserve`, either overpaying traders (draining more real LT/tokens than the pair actually received) or underpaying them, permanently.
- Graduation math (`_prepareGraduationLiquidity`) reads these same stored reserves to compute `ltFromPair` and `tokensForLP`, so the corrupted reserves would either lock a wrong-priced LP or attempt to drain more LT than the pair actually holds via `Router.graduate`, which itself just calls `Pair.transferAsset` with an unchecked `safeTransfer` of an amount that may exceed the real balance and revert (bricking graduation) or, in a different divergence direction, leave real value permanently stuck.
This qualifies as a High-severity finding under the contest's criteria (concrete theft/freezing of trader and creator funds, LP seeded away from the true curve close price) if the underlying assumption that the LT's `transferFrom` always delivers exactly the requested amount is ever violated.

### Likelihood Explanation
Likelihood is Low in the current system, mirroring the original report's own "Likelihood: 1" rating. The LT is a fixed, protocol-controlled integration point (BounceTech's `LeveragedToken`), documented throughout the codebase as rebasing only via `exchangeRate()` (an accounting view), not via per-transfer fee/burn mechanics, and `Token.sol` (the launched token) is a plain OZ ERC20 clone with no transfer hooks. So under the *current* implementations of both assets, nominal transfer amount always equals the balance delta. The vulnerability is latent/defense-in-depth: it would only be realized if BounceTech redeploys/upgrades the LT with any transfer-side friction, or if a future LT integration deviates from a pure ERC20. There is no way for an unprivileged trader to force this divergence today since they don't control the LT/Token contracts' transfer semantics.

### Recommendation
Mirror the report's fix pattern: in `Router.buy`/`Router.sell` (and `Router.graduate`), read `IERC20(asset).balanceOf(pairAddr)` (or `IERC20(token).balanceOf(pairAddr)`) immediately before and after the `safeTransferFrom`, and pass the *measured delta* — not the nominal `amountInUsed`/`amountIn` — into `Pair.swap()`'s reserve bookkeeping. This ensures `_pool.assetReserve`/`tokenReserve` can never diverge from the pair's real balances regardless of how the reserve asset's transfer semantics evolve.

### Proof of Concept
Conceptual (cannot be triggered against the current LT/Token implementations, which are plain ERC20s with no transfer friction):
1. Assume a future BounceTech LT redeploy (or any LT the protocol whitelists via `Bonding.launch`'s `ltExists` gate) implements a small transfer fee/burn-on-transfer.
2. A trader calls `Zap.buy(token, usdcAmount, 0, referrer)`. `Zap` mints LT and calls `Bonding.buy` → `Router.buy`, which does `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`.
3. The pair actually receives `amountInUsed - fee` LT, but `Router.buy` still calls `IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0)`, crediting the pair's stored `assetReserve` with the full nominal `amountInUsed`.
4. `_pool.assetReserve` is now `fee` higher than the pair's real LT balance. Every subsequent trade is priced off this inflated reserve, and graduation's `ltFromPair = assetReserve - virtualLtReserve` overstates the real LT raised, causing `Router.graduate` to attempt to drain more LT than the pair holds (`Pair.transferAsset`'s `safeTransfer` would then either revert, bricking graduation, or — if enough surplus LT had accumulated from other trades — silently pay out LT that was never actually raised, at other traders' expense).

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

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L1-49)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title IBounceLeveragedToken
/// @notice Interface for BounceTech Leveraged Token contracts.
/// @dev Source:
///      https://github.com/bounce-tech/bounce-smart-contracts/blob/main/src/LeveragedToken.sol
interface IBounceLeveragedToken is IERC20 {
    /// @notice USDC → LT.
    function mint(
        address to,
        uint256 baseAmount,
        uint256 minOut
    ) external returns (uint256 ltAmount);

    /// @notice LT → USDC. Reverts if the computed USDC output exceeds `baseAssetBalance()`.
    function redeem(
        address to,
        uint256 ltAmount,
        uint256 minBase
    ) external returns (uint256 baseAmount);

    /// @notice Idle USDC available for atomic redeem.
    function baseAssetBalance() external view returns (uint256);

    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);

    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);

    /// @notice Inverse of `baseToLtAmount`. The round-trip
    ///         `baseToLtAmount(ltToBaseAmount(x))` may differ from `x` by 1
    ///         wei due to integer-division rounding.
    function ltToBaseAmount(
        uint256 ltAmount
    ) external view returns (uint256);

    function targetLeverage() external view returns (uint256);

    function isLong() external view returns (bool);

    function underlyingSymbol() external view returns (string memory);
}
```
