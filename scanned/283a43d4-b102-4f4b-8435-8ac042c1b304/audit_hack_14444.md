# [M] `abi.encodePacked` causes collisions that can lead to same  `tokenURI` returned for different `tokenID`s

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol
Type: audit-issue

## Details
# `abi.encodePacked` causes collisions that can lead to same  `tokenURI` returned for different `tokenID`s

## Summary
From the [`solidity documentation`](https://docs.soliditylang.org/en/v0.8.17/abi-spec.html?highlight=collisions#non-standard-packed-mode): --> If you use `abi.encodePacked(a, b)` and both `a` and `b` are dynamic types, it is easy to craft collisions in the hash value by moving parts of `a` into `b` and vice-versa. More specifically, `abi.encodePacked("a", "bc") == abi.encodePacked("ab", "c")`. This Issue is seen in the [`MeritNFT sol`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol) where the `tokenURI` would return same `URI` for different `tokenID`s.
## Vulnerability Detail
You can see in the `tokenURI` function in `MeritNFT.sol`
```solidity
function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");

        string memory baseURI_ = _baseURI();
        return bytes(baseURI_).length > 0 ? string(abi.encodePacked(baseURI_, tokenId.toString(), ".json")) : "";
    }
```
Here it checks if the `baseURI` is greater than `0` and returns the `abi.encodePacked(baseURI_, tokenId.toString(), ".json"))`, you can see that the type are of `string` and the can be dynamic. As the `solidity docs` describe, two or more dynamic types are passed to `abi.encodePacked`, the return type would be same, and if a situation like that occurs Same `tokenURI` would be returned for different `tokenID`s whose `baseURI`, `tokenid.toString()`, and `json` are of dynamic types.

## Impact
This would be a `medium` as the chances are low but the Impact would be so high as the `tokenID` of different `NFT`s would return the same Image when they are suppose to be different, thereby hurting the value of the `NFT`s, Also `NFT` marketplaces will fetch this wrong data from that `tokenURI`and display the data on their site causing issues with different `NFTs` having same images as their tokenURI is same but different `tokenID` thereby causing corruption to the data of the `NFT`s .

## Code Snippet
- `Line with Bug` ●---> [Click here](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L101)
## Tool used

`Manual Review`

## Recommendation
Use `abi.encode` instead as it doesn't return same values for different dynamic types or put a constant value in-between the values being `encoded`
