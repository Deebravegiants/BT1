# [M] DoS if NFT is minted outside mistakenly

## Summary
Severity: Medium
Reporter: ww4tson
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L159
Type: audit-issue

## Details
# DoS if NFT is minted outside mistakenly

## Summary
If MeritNFT is minted mistakenly outside of MeritDutchAuction, then the Auction will be stuck permanently.

## Vulnerability Detail
MeritDutchAuction assumes that none of MeritNFT is minted outside of the auction (itself).

```solidity
    function mint(uint256 amount) external payable {

        uint256 mintedBefore = minted;
        ...
        minted += amount;
        ...

        for(uint256 i = 0; i < amount; i++) {
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
Above is the redacted relevant code. In `ntf.mint`, the `id` is incremented starting from 1.
This is too rigid and if any nft is minted outside the auction, mint will be failed due to duplicated `id`. Furthermore, `nft` is only settable once.

## Impact
Auction contract will become useless forever.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L159

## Tool used

Manual Review

## Recommendation
Give a little more room by specifying `startId`. Admin can always get `startId` from contract's `minted` variable if needed.
```solidity
    function mint(uint256 amount, uint256 startId) external payable {

        uint256 mintedBefore = minted;
        ...
        minted += amount;
        ...

        for(uint256 i = 0; i < amount; i++) {
            nft.mint(mintedBefore + i + 1 + startId, msg.sender);
        }
```
