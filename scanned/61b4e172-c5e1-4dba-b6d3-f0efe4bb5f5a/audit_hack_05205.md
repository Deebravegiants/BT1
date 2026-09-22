# [M] OngoingBountyV1 is incompatible with NFTs but still accepts NFT deposits

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-openq/blob/main/contracts/Bounty/Implementations/OngoingBountyV1.sol#L133-L160
Type: audit-issue

## Details
# OngoingBountyV1 is incompatible with NFTs but still accepts NFT deposits

## Summary

OngoingBountyV1 is incompatible with NFTs but still accepts NFT deposits

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-openq/blob/main/contracts/Bounty/Implementations/OngoingBountyV1.sol#L133-L160

OngoingBountyV1 is designed to receive NFTs and NFTs can be deposited to it via DepositManager#fundBountyNFT

https://github.com/sherlock-audit/2023-02-openq/blob/main/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L173-L197

However when ongoing bounties are claimed they have no method to distribute the NFTs that are deposited.

## Impact

OngoingBountyV1 has no way to distribute NFTs

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/main/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L173-L197

## Tool used

Manual Review

## Recommendation

Change _claimOngoingBounty to allow it to distribute NFTs
