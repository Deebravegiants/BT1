# [M] The `CAP_PER_ADDRESS` Restriction Can Be Bypassed

## Summary
Severity: Medium
Reporter: ubermensch
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143
Type: audit-issue

## Details
# The `CAP_PER_ADDRESS` Restriction Can Be Bypassed

## Summary
The issue in the `mint` function of the smart contract, specifically related to the `CAP_PER_ADDRESS` restriction. This restriction can be easily bypassed, breaking the invariant of each address having less than the `CAP_PER_ADDRESS`.

## Vulnerability Detail
The contract uses the `mintedPerAddress` to track the minted tokens per account. However, this condition can be easily bypassed by using multiple wallets and then transferring the tokens to the same account. This would result in an account holding more tokens than the `CAP_PER_ADDRESS` limit.

## Impact
The impact of this vulnerability is significant. It allows an individual to hold more tokens than intended by the `CAP_PER_ADDRESS` limit, potentially leading to an imbalance in token distribution and power within the network. This could undermine the fairness and security of the system.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143

## Tool used
Manual Review

## Recommendation
To mitigate this vulnerability, consider implementing a mechanism that tracks the total tokens held by an account, including those received through transfers. This would ensure that the `CAP_PER_ADDRESS` limit is enforced not just at the minting stage, but throughout the lifecycle of the token.
