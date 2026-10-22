# [M] M-06 | Bump Reverts Due To Lack Of Reserves

## Summary
Severity: Medium
Contest weight: 0.4033
Dataset id: 21486
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An edge case appears when the price is at DISCOVERY range, and all reserves from FLOOR and ANCHOR are borrowed. This could happen when there is heavy buying, and all bAssets are collateralized. If we try to trigger a bump operation, this will revert at this function: BPOOL.manageLiquidityFor(Range.DISCOVERY, Action.ADD, liquidityD); The issue is that when we try to mint liquidity in the Uniswap Pool, the calculation for the token amounts owed to the pool are rounded up: getAmount1Delta(sqrtRatioAX96, sqrtRatioBX96, uint128(liquidity), true). Due to the rounding up, more reserves are requested to be transferred in the uniswapV3MintCallback than available, preventing the bump operation from occurring.

## Recommendation
Prevent the DoS by ensuring that no more reserves are requested for the DISCOVERY range than available:
```solidity
uint256 reservesNeeded = LiquidityAmounts.getAmount1ForLiquidity(
    discovery.sqrtPriceL,
    sqrtPriceA > discovery.sqrtPriceU ? discovery.sqrtPriceU : sqrtPriceA,
    liquidityD
);
uint256 reserveBal = BPOOL.reserve().balanceOf(address(BPOOL));
if (activeTick > discL && liquidityF == 0) BPOOL.manageReservesFor(Range.DISCOVERY, Action.ADD, reservesNeeded > reserveBal ? reserveBal : reservesNeeded);
else BPOOL.manageLiquidityFor(Range.DISCOVERY, Action.ADD, liquidityD);
```
