Audit Report

## Title
Token Decimal Normalization Missing in `viewSwapRsETHAmountAndFee` Causes Near-Zero wrsETH Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

## Summary

`viewSwapRsETHAmountAndFee(uint256 amount, address token)` in both `RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge` computes the wrsETH mint amount as `amountAfterFee * tokenToETHRate / rsETHToETHrate` without normalizing `amountAfterFee` from the token's native decimal precision to 18 decimals. For any supported token with fewer than 18 decimals (e.g., USDC at 6, WBTC at 8), the minted wrsETH amount is `10^(18 − tokenDecimals)` times too small. The deposited tokens are permanently locked in the pool with no user-accessible recovery path, constituting permanent freezing of user funds.

## Finding Description

**Root cause — missing decimal normalization in the token deposit path:**

The ETH deposit path in `RSETHPoolV3.sol` correctly handles precision:

```solidity
// L307
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

`amountAfterFee` is already in 1e18 (wei) precision, and the explicit `* 1e18` keeps the result in 1e18 wrsETH units given that `rsETHToETHrate` is also 1e18-scaled.

The token deposit path in both contracts omits this normalization:

```solidity
// RSETHPoolV3.sol L334
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;

// RSETHPoolV3WithNativeChainBridge.sol L370
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` (from `IOracle(supportedTokenOracle[token]).getRate()`) returns the price of **one full token** in ETH, 1e18-scaled (e.g., 1 USDC ≈ 4×10¹⁴ wei of ETH). `rsETHToETHrate` is similarly 1e18-scaled. When `amountAfterFee` is in the token's native decimals (e.g., 1e6 units for 1 USDC), the formula produces a result that is `10^(18 − tokenDecimals)` times too small.

**Dimensional analysis:**

Correct formula:
```
rsETHAmount = (amountAfterFee / 10^tokenDecimals) * (tokenToETHRate / 1e18) / (rsETHToETHrate / 1e18) * 1e18
            = amountAfterFee * tokenToETHRate * 1e18 / (10^tokenDecimals * rsETHToETHrate)
```

Actual formula:
```
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate
```

The missing factor is `1e18 / 10^tokenDecimals = 10^(18 − tokenDecimals)`.

**Exploit path:**

1. Admin calls `addSupportedToken(USDC, usdcOracle)` — USDC (6 decimals) is listed.
2. Any user calls `deposit(USDC, 1_000e6, "ref")` — transfers 1,000 USDC to the pool.
3. `viewSwapRsETHAmountAndFee(1_000e6, USDC)` computes: `1_000e6 * 4e14 / 1.05e18 ≈ 380,952 wei` of wrsETH.
4. User receives `≈ 381,000 wei` wrsETH instead of `≈ 380.95e18 wei` — a factor of `10^12` shortfall.
5. The 1,000 USDC remains in the pool. There is no `withdraw`, `redeem`, or user-callable recovery function in either contract. `swapAssetToPremintedRsETH` is restricted to `OPERATOR_ROLE`.

**Existing guards are insufficient:**

- `onlySupportedToken` only checks that the token has a registered oracle — no decimal restriction.
- `limitDailyMint` calls the same broken `viewSwapRsETHAmountAndFee`, so the daily cap is also effectively bypassed (the computed rsETH amount is negligible, never triggering `DailyMintLimitExceeded`).
- `nonReentrant` and `whenNotPaused` are irrelevant to this accounting error.

## Impact Explanation

**Critical — Permanent freezing of user funds.**

A user depositing any supported non-18 decimal token (USDC, WBTC, etc.) transfers their full token balance to the pool and receives a near-zero wrsETH amount. Because neither contract exposes a user-callable withdrawal or redemption path, the deposited tokens are permanently inaccessible to the user. The loss is immediate, irreversible, and proportional to the deposit size.

## Likelihood Explanation

`addSupportedToken` in both contracts accepts any ERC-20 address with no decimal restriction. Both pools are deployed on L2 chains where USDC (6 decimals) and WBTC (8 decimals) are standard bridged assets and natural candidates for inclusion. Once any such token is listed, any unprivileged depositor who calls `deposit(token, amount, referralId)` triggers the loss immediately with no further preconditions. The function is public, non-restricted, and callable by any EOA or contract.

## Recommendation

Normalize `amountAfterFee` to 18-decimal precision before applying the rate formula, mirroring the ETH path. Apply the fix to both `viewSwapRsETHAmountAndFee(uint256, address)` in `RSETHPoolV3.sol` and `RSETHPoolV3WithNativeChainBridge.sol`, and to the inverse direction in `viewSwapAssetToPremintedRsETH` in both contracts:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

// In viewSwapRsETHAmountAndFee(uint256 amount, address token):
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;

// In viewSwapAssetToPremintedRsETH(address token, uint256 rsETHAmount):
uint8 tokenDecimals = IERC20Metadata(token).decimals();
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate / 10 ** (18 - tokenDecimals);
```

## Proof of Concept

**Setup:** USDC (6 decimals) added as supported token; oracle returns `4e14` (≈ 0.0004 ETH per USDC); rsETH oracle returns `1.05e18`.

**Call sequence:**
```solidity
// 1. Admin lists USDC
pool.addSupportedToken(USDC, usdcOracle); // TIMELOCK_ROLE

// 2. User deposits 1,000 USDC
usdc.approve(address(pool), 1_000e6);
pool.deposit(USDC, 1_000e6, "ref");
```

**Execution trace:**
```
amountAfterFee = 1_000e6          // feeBps = 0 for simplicity
tokenToETHRate = 4e14
rsETHToETHrate = 1.05e18

rsETHAmount = 1_000e6 * 4e14 / 1.05e18
            = 4e23 / 1.05e18
            ≈ 380,952 wei         // ~0.000000000000381 wrsETH minted
```

**Expected:**
```
normalizedAmount = 1_000e6 * 1e12 = 1_000e18
rsETHAmount = 1_000e18 * 4e14 / 1.05e18 ≈ 380.95e18 wei  // ~380.95 wrsETH
```

**Foundry test plan:**
```solidity
function testUSDCDepositDecimalMiscalculation() public {
    // Deploy mock USDC (6 decimals), mock oracle returning 4e14, rsETH oracle returning 1.05e18
    // addSupportedToken(usdc, usdcOracle)
    // deal(usdc, user, 1_000e6); vm.prank(user); usdc.approve(pool, 1_000e6);
    // vm.prank(user); pool.deposit(usdc, 1_000e6, "ref");
    uint256 minted = wrsETH.balanceOf(user);
    assertLt(minted, 1e6, "received near-zero wrsETH");
    // Expected: ~380.95e18; Actual: ~380952 wei
    assertEq(IERC20(usdc).balanceOf(address(pool)), 1_000e6, "USDC locked in pool");
    // User has no way to recover the USDC
}
```

The 1,000 USDC deposited is permanently locked in the pool; the user receives `≈ 381,000 wei` of wrsETH instead of `≈ 380.95e18 wei` — a `10^12` shortfall with no recovery path.