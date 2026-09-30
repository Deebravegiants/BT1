# [M] User can mint NFTs after the auction end

## Summary
Severity: Medium
Reporter: 0xhuy0512
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128C1-L147C3
Type: audit-issue

## Details
# User can mint NFTs after the auction end

## Summary
User can mint NFTs after the auction end
## Vulnerability Detail
There's no requirement check if timestamp is passing endTime in `mint()`
## Impact
This make user can mint NFTs after the auction end
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128C1-L147C3
## Tool used

Manual Review

## Recommendation
Add requirement check in `mint()`
