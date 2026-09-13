# [H] setPoolActive() function missing onlyPoolManager(msg.sender)

## Summary
Severity: High
Reporter: Low Corduroy Cow
Source: https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/strategies/rfp-simple/RFPSimpleStrategy.sol#L219
Type: audit-issue

## Details
# setPoolActive() function missing onlyPoolManager(msg.sender)

`setPoolActive()` function missing `onlyPoolManager(msg.sender)` ,it will cause anyone to set the pool acitve status.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/strategies/rfp-simple/RFPSimpleStrategy.sol#L219

## Impact

it will cause anyone to set the pool acitve status.

## Code Snippet

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/strategies/rfp-simple/RFPSimpleStrategy.sol#L219

## Tool used

Manual Review

## Recommendation

add `onlyPoolManager(msg.sender)`
