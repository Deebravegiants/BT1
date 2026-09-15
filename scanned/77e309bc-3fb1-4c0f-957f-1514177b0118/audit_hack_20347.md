# [M] 5.3.3 UNI_V3Validatorfetches spot prices that may lead to price manipulation attacks

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** UNI_V3Validator.sol#L126-L130
**Description:** UNI_V3Validator.validateAndParse()checks the state of the Uniswap V3 position. This includes
checking the LP value throughLiquidityAmounts.getAmountsForLiquidity.
//get pool state
//get slot 0
(uint160 poolSQ96, , , , , , ) = IUniswapV3PoolState(
V3_FACTORY.getPool(token0, token1, fee)
).slot0();
(uint256 amount0, uint256 amount1) = LiquidityAmounts
.getAmountsForLiquidity(
poolSQ96,
TickMath.getSqrtRatioAtTick(tickLower),
TickMath.getSqrtRatioAtTick(tickUpper),
liquidity
);

- LiquidityAmounts.sol#L177-L221
When we deep dive intogetAmountsForLiquidity, we see three cases. Price is below the range, price is within
the range, and price is above the range.


```
function getAmountsForLiquidity(
uint160 sqrtRatioX96,
uint160 sqrtRatioAX96,
uint160 sqrtRatioBX96,
uint128 liquidity
) internal pure returns (uint256 amount0, uint256 amount1) {
unchecked {
if (sqrtRatioAX96 > sqrtRatioBX96)
(sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96);
if (sqrtRatioX96 <= sqrtRatioAX96) {
amount0 = getAmount0ForLiquidity(
sqrtRatioAX96,
sqrtRatioBX96,
liquidity
);
} else if (sqrtRatioX96 < sqrtRatioBX96) {
amount0 = getAmount0ForLiquidity(
sqrtRatioX96,
sqrtRatioBX96,
liquidity
);
amount1 = getAmount1ForLiquidity(
sqrtRatioAX96,
sqrtRatioX96,
liquidity
);
} else {
amount1 = getAmount1ForLiquidity(
sqrtRatioAX96,
sqrtRatioBX96,
liquidity
);
}
}
}
```
For simplicity, we can break intogetAmount1ForLiquidity


```
/// @notice Computes the amount of token1 for a given amount of liquidity and a price range
/// @param sqrtRatioAX96 A sqrt price representing the first tick boundary
/// @param sqrtRatioBX96 A sqrt price representing the second tick boundary
/// @param liquidity The liquidity being valued
/// @return amount1 The amount of token1
function getAmount1ForLiquidity(
uint160 sqrtRatioAX96,
uint160 sqrtRatioBX96,
uint128 liquidity
) internal pure returns (uint256 amount1) {
unchecked {
if (sqrtRatioAX96 > sqrtRatioBX96)
(sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96);
return
FullMathUniswap.mulDiv(
liquidity,
sqrtRatioBX96 - sqrtRatioAX96,
FixedPoint96.Q96
);
}
}
```
We find the amount is calculated as amount = liquidity * (upper price - lower price). When the
slot0.poolSQ96is in lp range, the lower price is theslot0.poolSQ96, the closer slot0 is tolowerTick, the
smaller theamount1is.
This is vulnerable to price manipulation attacks asIUniswapV3PoolState.slot0.poolSQ96is effectively the spot
price. Attackers can acquire huge funds through flash loans and shift theslot0by doing large swaps onUniswap.
Assume the following scenario, the strategist sign a lien that allows the borrower to provideETH-USDCposition with
>1,000,000USDC and borrow 1,000,000 USDC from the vault.

- Attacker can first provides 1 ETH worth of lp at price range2,000,000 ~ 2,000,001.
- The attacker borrows flash loan to manipulate the price of the pool and now the slot0.poolSQ96 =
    sqrt(2,000,000). (ignoring the decimals difference.
- getAmountsForLiquidityvalue the LP positions with the spot price, and find the LP has1 * 2,000,000
    USDC in the position. The attacker borrows2,000,000
- Restoring the price ofUniswappool and take the profit to repay the flash loan.
Note that the project team has stated clearly thatUNI_V3Validatorwill not be used before the audit. This issue is
filed to provide information to the codebase.
**Recommendation:** Fetch price from a reliable price oracle instead ofslot0. Also, it is recommended to document
the risk ofUNI_V3Validatorin the codebase or documentation.
