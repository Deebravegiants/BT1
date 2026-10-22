# [H] Allowing native coin to be deposited results in native coin being stuck in the contract forever.

## Summary
Severity: High
Reporter: caventa
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueProxy.sol#L46
Type: audit-issue

## Details
# Allowing native coin to be deposited results in native coin being stuck in the contract forever.

## Summary
Allowing native coin to be deposited results in native coin being stuck in the contract forever.

## Vulnerability Detail
The queue proxy contract and auction proxy contract allows native coin to be deposited (See QueueProxy.sol#L46 and AuctionProxy.sol#L33) but there is no code available to allow native coin to be used or to be withdrawn.

## Impact
Ether may be stuck in the contract forever.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueProxy.sol#L46
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L33

## Tool used
Manual Review

## Recommendation
None
