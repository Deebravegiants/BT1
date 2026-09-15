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
        ) + receiveAmount;
```

The problem occurs when pure collateral is enough to cover the payment, while the lending shares portion can not be currently covered by the pool. Even thought the liquidator could be made whole immediately (by drawing from the pure collateral first and only then drawing from the lendind shares) they will receive only part of their due payment (which might not even cover the debt they paid back) and the rest in shares that can not be withdrawn immediately, adding an unwanted risk to liquidators and possibly preventing liquidations.


# Attack scenario

- Alice borrows a certain amount of token A, collateralized by token B made of 750 Eth worth of pure collateral token B, and 250 Eth worth of Token B lending shares.
- At some point the value of the borrowed token A rises to 700 Eth, which is above the weighted Eth value of the 1000 Eth full collateral (assuming a collateral weight of 70% for token B) making Alice's position liquidatable.
 - Bob sends a transaction to liquidize Alice's position, paying back 700 Eth in Token A. Bob should receive 735 Eth of token B (assuming a 5% liquidation incentive).
 - The full value of collateral (unweighted) is 1000 Eth, makeing Bob's payment 73.5% of the full collateral.
 - Liquidation logic takes 73.5% of the pure collateral (551.25 Eth worth of Token B) and 73.5% of the lending shares (worth 220.5 Eth)
 - If at the time of liquidation the Token B pool only has 50 Eth worth of token B, Bob will have to take 170.5 eth worth of Token B as shares in the pool, to be redeemable only when the pool reserves are re-filled.
 - This is inspite of the fact that the pure Token B collateral (worth 750 Eth) can cover the full Token B Bob should receive
 - This creates an economic loss to both liquidators and pool users. Liquidators might only immediately get part of the value of debt they repaid, let alone the incentive, and are forced to take a risk in the form of postponed payment. For pool lenders the effect is increased bad debt risk given that liquidators might avoid liquidating positions in this scenario.

# Recommendation

The liquidation logic can be changed to draw the liquidation collateral payment from the pure collateral first (up to the total amount of pure collateral) and only then draw from the lending shares. If the full amount can be covered by pure collateral entirely, this would also save gas on the liquidation transaction.


# POC

To be added in comments by competition end.
