# [H] Significant rounding errors due to gameETH not having precision

## Summary
Severity: High
Contest weight: 0.1767
Dataset id: 6638
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UP-H01 Significant rounding errors due to gameETH not having precision up::addGameETH() and Codeup::reinvest(), gameETH is obtained as gameETH = amount / gameETHPrice, which means there may be rounding errors. gameETH has no up::_getUpgradePrice() and up::_getYield(), which have no extra precision. Thus, as gameETHPrice may be a big value - currently 1e12 in the tests, the rounding error may be up to 1e12 - 1, which is approx 0.0023 USD. If the price is increased, the rounding error grow to bigger values causing significant loss of funds for users. up::_getUpgradePrice() and Codeup::_getYield() and decreasing the gameETHPrice so gameETH inherits the decimals of ETH.

## Recommendation
Add some precision to gameETH by scaling the values in the functions
