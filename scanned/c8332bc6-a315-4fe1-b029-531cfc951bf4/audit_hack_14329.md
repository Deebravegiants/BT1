# [H] The baseURI can be changed by the URI setter after the auction is completed

## Summary
Severity: High
Reporter: ast3ros
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L67-L69
Type: audit-issue

## Details
# The baseURI can be changed by the URI setter after the auction is completed

## Summary

There is no restriction on the baseURI setter. The baseURI can be changed after the auction is completed.

## Vulnerability Detail

The `setBaseURI` function can be called by `onlyUriSetter` at any time.

        function setBaseURI(string memory _newBaseURI) external onlyUriSetter {
            baseTokenURI_ = _newBaseURI;
        }

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L67-L69

Because there are no traits of NFT stored on chain, the value of the NFTs depends on their metadata which includes critical information such as traits, rarity, images, etc. If the `baseURI` is changed after the auction is completed, the value of the NFTs can be affected.

In this contest, the `URI setter` is not a trusted party and has the potential to change the `baseURI` after the auction is completed without NFT owner’s consent. This can cause the NFT owner to lose their NFTs’ value if the `baseURI` is changed to a different value.

## Impact

NFT owners can lose their NFTs’ value.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L67-L69

## Tool used

Manual Review

## Recommendation

Only allow the URI setter to set the baseURI once after the NFT contract is deployed.

```diff
    function setBaseURI(string memory _newBaseURI) external onlyUriSetter {
+       require(keccak256(abi.encodePacked(baseTokenURI_)) == keccak256(abi.encodePacked("")), "BaseURI is already set");
        baseTokenURI_ = _newBaseURI;
    }
```
