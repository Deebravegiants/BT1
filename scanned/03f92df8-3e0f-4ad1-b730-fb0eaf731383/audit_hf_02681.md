# [H] Incorrect Calculation Of minterCollateral

## Summary
Severity: High
Contest weight: 0.7770
Dataset id: 14534
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Following discussions with the development team, it was established that the calculation of minterCollateral within
the function _mint() is incorrect. This will in turn produce incorrect calculations of trading fees and of the permitted
collateral ratios between the user and the market maker.
This is the original calculation:
LeverageDNTVault.sol
uint256 minterCollateral = (totalCollateral - params.makerCollateral) * APR_BASE / (APR_BASE + LEVERAGE_RATIO * APR_BASE +
LEVERAGE_RATIO * borrowAPR * (params.expiry - block.timestamp) / SECONDS_IN_YEAR);
Each time that a product is minted, the borrowFee and spreadFee will be incorrectly calculated as these variables are
derived from minterCollateral.
The correct calculation is derived from the following equation:
LeverageDNTVault.sol
// (totalCollateral - makerCollateral) = minterCollateral
+ minterCollateral * LEVERAGE_RATIO * borrowAPR / SECONDS_IN_YEAR *
(expiry - block.timestamp)
The left hand side of this equation is the amount of collateral provided by the user.
The right hand side is a calculation of a simulation of leverage. It consists of a nominal amount of collateral provided
by the user (minterCollateral) added to the borrow interest on borrowing that amount again LEVERAGE_RATIO times
for the active duration of the minted product.
From this equation, the correct calculation can be derived:
LeverageDNTVault.sol
uint256 minterCollateral = (totalCollateral - params.makerCollateral) * APR_BASE /
(APR_BASE + LEVERAGE_RATIO * borrowAPR * (params.expiry - block.timestamp) / SECONDS_IN_YEAR);
```

## Recommendation
After discussions with the development team, it was established that the calculation of the minterCollateral should
be revised to:
```solidity
LeverageDNTVault.sol
// (totalCollateral - makerCollateral) = minterCollateral
+ minterCollateral * LEVERAGE_RATIO * borrowAPR / SECONDS_IN_YEAR *
(expiry - block.timestamp)
uint256 minterCollateral = (totalCollateral - params.makerCollateral) * APR_BASE /
(APR_BASE + LEVERAGE_RATIO * borrowAPR * (params.expiry - block.timestamp) / SECONDS_IN_YEAR);
Sofa Protocol Contract Review
```
