# [H] MJR-1 Decrease in the amount of tokens during exchange due to arithmetic

## Summary
Severity: High
Contest weight: 0.0614
Dataset id: 179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the lines:
UnoswapV3Router.sol#L166 и
UnoswapV3Router.sol#L175
a number with the type uint256 is converted to a number with the type int256. This number is passed in the function parameter and, after conversion, is sent to the UniswapV3Pool contract.
But, if the value of the number is greater than the maximum value for the type int256, an arithmetic overflow will occur.
This is demonstrated by the following example: https://gist.github.com/mixbytes-audit/b471cc82105f856d1546ba638de20f4e.
For example, if you take the number 57896044618658097711785492504343953926634992332820282019728792003956564819970, then after the conversion you get the value-
We see a decrease in modulus of the initial value of the variable.

## Recommendation
Before lines 166 and 175, you need to check that the value of the number is less than the maximum value for the type int256.
