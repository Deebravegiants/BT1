# [M] User's money may be wasted on an unwanted NFT

## Summary
Severity: Medium
Reporter: Juntao
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10
Type: audit-issue

## Details
# User's money may be wasted on an unwanted NFT

## Summary

User's money may be wasted on an unwanted NFT.

## Vulnerability Detail

As non-fungible token, every [MeritNFT](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10) object has its own uniqueness value, so some may be wanted by an individual and some may be not.

Users can pay ether and mint NFTs through [mint(...)](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169) method, the certain NFT object to be minted could be predicted by `mintedBefore + i + 1`.

Let's assume:
1. Alice is fond of **NFT#10**, she waits till 9 NFTs have been minted and then submits a transaction to mint, expecting **NFT#10** to be minted to her.
2. However, Bob also wants **NFT#10**, so he submits the same transaction but with more gas fee, Bob's transaction gets executed before Alice's, **NFT#10** is minted to Bob. 
3. Alice's transaction gets executed then, what Alice get is **NFT#11** instead of a refund, her money is wasted on a NFT that she doesn't want.

## Impact

User's money is wasted.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

User bids on an auction to buy the desired NFT, the worst case should be a failed bid, not wasting money.

It is recommended to allow users specify the NFT tokenId they want to mint, and transaction should be reverted if the actual tokenId is different:
```diff
-   function mint(uint256 amount) external payable {
+   function mint(uint256 amount, uint256 expectedTokenId) external payable {
        // Checks
        // Cache mintedBefore to save on sloads
        uint256 mintedBefore = minted;

+      require(expectedTokenId == 0 ||  expectedTokenId == mintedBefore + 1)

        ...
    }
```
