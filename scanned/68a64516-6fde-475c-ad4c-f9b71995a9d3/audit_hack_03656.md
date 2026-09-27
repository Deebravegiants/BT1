# [M] FeeBuyback doesn't use safeTransferFrom for tokens transfering

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71
Type: audit-issue

## Details
# FeeBuyback doesn't use safeTransferFrom for tokens transfering

## Summary
FeeBuyback doesn't use safeTransferFrom for tokens transfering which may lead to silent failed transfers.

## Vulnerability Detail
FeeBuyback uses transferFrom to send erc20 tokens and doesn't check bool result of transfer. As result transfers can silently fail.
## Impact
Silent failed transfers can happen.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71
## Tool used

Manual Review

## Recommendation
Use safeTransferFrom as you do in another contracts.
