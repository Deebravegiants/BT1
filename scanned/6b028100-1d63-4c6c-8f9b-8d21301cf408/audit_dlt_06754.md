# [M] Unsafe cast in `getCollateralRatio()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-angle
Published: 2023-07-07
Source: https://github.com/code-423n4/2023-06-angle-findings/issues/31
Type: code-finding

## Details
# Lines of code

https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L87


# Vulnerability details

## Impact
`LibGetters.getCollateralRatio()` might return the incorrect ratio due to the unsafe cast.

## Proof of Concept
`getCollateralRatio()` outputs the collateral ratio using the total collaterals and issued agTokens.

```solidity
    // The `stablecoinsIssued` value need to be rounded up because it is then used as a divizer when computing
    // the amount of stablecoins issued
    stablecoinsIssued = uint256(ts.normalizedStables).mulDiv(ts.normalizer, BASE_27, Math.Rounding.Up);
    if (stablecoinsIssued > 0)
        collatRatio = uint64(totalCollateralization.mulDiv(BASE_9, stablecoinsIssued, Math.Rounding.Up)); //@audit unsafe cast
    else collatRatio = type(uint64).max;
```

Typically, the `collatRatio` should be around `BASE_9` but the ratio might be larger than `type(uint64).max` during the initial stage.

Furthermore, `totalCollateralization` is calculated using the [raw balance of collaterals](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L73) and it might be manipulated when [stablecoinsIssued](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L85) is not large.

Then [collatRatio](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L87) might be cast to the wrong value.

After all, `getCollateralRatio()` will return the wrong ratio and it will affect the protocol seriously.

## Tools Used
Manual Review

## Recommended Mitigation Steps
I think we should use the [SafeCast](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/facets/Swapper.sol#L9) library in [getCollateralRatio()](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L87).


## Assessed type

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-06-angle-findings/issues/31_
