# [M] `ExternalLending` - executing redemptions for fee-on-transfer tokens from AaveV3 will always revert

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-12-notional-update-5
Published: 2024-01-18
Source: https://github.com/sherlock-audit/2023-12-notional-update-5-judging/issues/65
Type: sherlock-finding

## Details
eol

high

# `ExternalLending` - executing redemptions for fee-on-transfer tokens from AaveV3 will always revert

## Summary
When the Treasury rebalances and has to redeem aTokens from AaveV3, it checks that the actual amount withdrawn is greater than or equal to the set `withdrawAmount`. This check will always fail for fee-on-transfer tokens since the `withdrawAmount` does not account for the transfer fee.

## Vulnerability Detail
When the Treasury rebalances and has to redeem aWETH from AaveV3 it executes calls that were encoded in `AaveV3HoldingsOracle._getRedemptionCalldata()`:
https://github.com/sherlock-audit/2023-12-notional-update-5/blob/main/contracts-v3/contracts/external/pCash/AaveV3HoldingsOracle.sol#L61-L81
```solidity
        address[] memory targets = new address[](UNDERLYING_IS_ETH ? 2 : 1);
        bytes[] memory callData = new bytes[](UNDERLYING_IS_ETH ? 2 : 1);
        targets[0] = LENDING_POOL;
        callData[0] = abi.encodeWithSelector(
            ILendingPool.withdraw.selector, underlyingToken, withdrawAmount, address(NOTIONAL)
        );

        if (UNDERLYING_IS_ETH) {
            // Aave V3 returns WETH instead of native ETH so we have to unwrap it here
            targets[1] = address(Deployments.WETH);
            callData[1] = abi.encodeWithSelector(WETH9.withdraw.selector, withdrawAmount);
        }

        data = new RedeemData[](1);
        // Tokens with less than or equal to 8 decimals sometimes have off by 1 issues when depositing
        // into Aave V3. Aave returns one unit less than has been deposited. This adjustment is applied
        // to ensure that this unit of token is credited back to prime cash holders appropriately.
        uint8 rebasingTokenBalanceAdjustment = UNDERLYING_DECIMALS <= 8 ? 1 : 0;
        data[0] = RedeemData(
            targets, callData, withdrawAmount, ASSET_TOKEN, rebasingTokenBalanceAdjustment
        );
```

Note that the third field in the `RedeemData` struct is the `expectedUnderlying` field which is set to the `withdrawAmount` and that `withdrawAmount` is a value greater than zero. 


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-12-notional-update-5-judging/issues/65_
