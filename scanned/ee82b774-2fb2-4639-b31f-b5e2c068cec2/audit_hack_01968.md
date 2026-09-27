# [H] 6.15 Possible DOS From First Depositor

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

The first user that calls deposit in ERC20RootVault can choose freely any amount (including zero) for
each vault token, while the LP shares are set to the largest amount by the following loop in
_getLpAmount:

```
for (uint256 i = 0; i < tvl_.length; ++i) {
if (amounts[i] > lpAmount) {
lpAmount = amounts[i];
}
}
```
However, if the first user (on initialization or whenever totalSupply is zero) chooses to deposit only
one token (e.g., token[0]) it makes impossible for other users to deposit other tokens (e.g., token[1])
as the totalSupply is not zero anymore, and _getNormalizedAmount considers the existing TVL:


```
// normalize amount
uint256 res = FullMath.mulDiv(tvl_, lpAmount, supply); // if tvl_ == 0, res = 0
```
The intended use of the function might be that the first deposit is done by a trusted account, but this is not
enforced.

Code corrected:

A new constant FIRST_DEPOSIT_LIMIT is introduced and a require checks that each token amount is
above this limit with tokenAmounts[i] > FIRST_DEPOSIT_LIMIT.
