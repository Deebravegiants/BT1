# [M] getUsersConfirmedButNotSettledSynthBalance is potentially calculated wrongly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-08
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/21
Type: code-finding

## Details
# Handle

0xImpostor


# Vulnerability details

## Impact

Incorrect tabulation of `getUsersConfirmedButNotSettledSynthBalance` will lead to the wrong balances returning. Fortunately, there are no important functions that are dependent on `balanceOf` so the impact of this erroneous calculation is limited.  

## Tools Used

Manual analysis

## Recommended Mitigation Steps

Line [528](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L528-L529) should be

```jsx
uint256 amountSyntheticTokensToBeShiftedAwayFromOriginSide
       = userNextPrice_syntheticToken_toShiftAwayFrom_marketSide[marketIndex][**isLong**][user];
```

Line [531](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L531) should be 

```jsx
if (amountSyntheticTokensToBeShiftedAwayFromOriginSide > 0) {
        uint256 syntheticTokenPriceOnOriginSide = syntheticToken_priceSnapshot[marketIndex][**isLong**][
          currentMarketUpdateIndex
        ];
        uint256 syntheticTokenPriceOnTargetSide = syntheticToken_priceSnapshot[marketIndex][**!isLong**][
          currentMarketUpdateIndex
        ];

        confirmedButNotSettledBalance += _getEquivalentAmountSyntheticTokensOnTargetSide(
          amountSyntheticTokensToBeShiftedAwayFromOriginSide,
          syntheticTokenPriceOnOriginSide,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/21_
