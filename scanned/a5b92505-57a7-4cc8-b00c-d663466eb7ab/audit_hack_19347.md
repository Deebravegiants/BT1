# [M] This contract does not prevent Ether deposits

## Summary
Severity: Medium
Reporter: Dancing Opaque Trout
Source: https://github.com/sherlock-audit/2024-01-rio-vesting-escrow/blob/main/rio-vesting-escrow/src/adaptors/OZVotingAdaptor.sol#L1-L93
Type: audit-issue

## Details
# This contract does not prevent Ether deposits

krkba
## Summary
The contract does not prevent Ether deposits.
## Vulnerability Detail
If someone sends Ether to this contract by mistake, it will be stuck unless the contract owner calls `recoverEther`.
## Impact
It leads to stuck of funds.
## Code Snippet
https://github.com/sherlock-audit/2024-01-rio-vesting-escrow/blob/main/rio-vesting-escrow/src/adaptors/OZVotingAdaptor.sol#L1-L93
## Tool used

Manual Review

## Recommendation
add a fallback function that reverts transactions with value.
