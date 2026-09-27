# [M] an unbounded loop can lead to a Dos

## Summary
Severity: Medium
Reporter: bulej93
Source: https://github.com/sherlock-audit/2023-02-kairos/blob/main/kairos-contracts/src/BorrowLogic/BorrowHandlers.sol#L112
Type: audit-issue

## Details
# an unbounded loop can lead to a Dos

## Summary
there is an unbounded loop that can lead to a denial of service attack
## Vulnerability Detail
in the function useCollateral there is a for loop that goes through each offer and calls the useOffer function which leads to funds transfer. malicious user can dump worthless nfts into the protocol which will lead to the loop exceeding the maximum gas limit
## Impact
the function will revert
## Code Snippet
https://github.com/sherlock-audit/2023-02-kairos/blob/main/kairos-contracts/src/BorrowLogic/BorrowHandlers.sol#L112
## Tool used

Manual Review

## Recommendation
