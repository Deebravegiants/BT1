# [M] FeeBuyback.submit and FeeBuyback.rescueERC20 modifiers should be switched

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47
Type: audit-issue

## Details
# FeeBuyback.submit and FeeBuyback.rescueERC20 modifiers should be switched

## Summary
FeeBuyback.submit and FeeBuyback.rescueERC20 modifiers should be switched
## Vulnerability Detail
FeeBuyback.submit uses onlyOwner modifier and FeeBuyback.rescueERC20 uses onlyExecutor modifier.
This modifiers should be switched for this functions, FeeBuyback.submit should use onlyExecutor and FeeBuyback.rescueERC20 should use onlyOwner.
## Impact
Functions can be called by roles that should not be able to.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94
## Tool used

Manual Review

## Recommendation
Switch modifiers for functions.
