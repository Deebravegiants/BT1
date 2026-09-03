# [M] Liquidators may receive pool shares instead of collateral even when enough pure collateral exists to cover their payment

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-08
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/15
Type: hats-finding

## Details
**Github username:** @nirohgo
**Twitter username:** niroh30
**Submission hash (on-chain):** 0x8bf1ff31ad1f436f8b5cf30b910d908b94cbd2c87e66d65b0ba6b118fc6fd4bb
**Severity:** medium

**Description:**
# Description

The liquidation logic uses the following process to source collateral funds to re-pay the liquidator:
1. Calculates the required percentage of the position's full collateral (pure collateral + lending shares collateral) required to cover the liquidator payment (including the value of the paid debt and the incentive).
```solidity
uint256 collateralPercentage = WISE_SECURITY.calculateWishPercentage(
            _data.nftId,
            _data.tokenToRecieve,
            WISE_ORACLE.getTokensInETH(
                _data.tokenToPayback,
                _data.paybackAmount
            ),
            _data.maxFeeETH,
            _data.baseRewardLiquidation
        );
```
2. Take the calculated ratio from the pure collateral
```solidity
uint256 receiveAmount = _withdrawPureCollateralLiquidation(
            _nftId,
            _receiveTokens,
            _removePercentage
        );
```
3. Take the calculated ratio from the lending shares collateral.
4. If the collateral pool does not have enough liquidity available to pay its share, the liquidator gets the missing part as pool shares.
```solidity
return _withdrawOrAllocateSharesLiquidation(
            _nftId,
            _nftIdLiquidator,
            _receiveTokens,
            _removePercentage
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/15_
