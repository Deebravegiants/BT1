# [M] `MeritNFT` can be minted by contracts that are unable to handle them

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
Type: audit-issue

## Details
# `MeritNFT` can be minted by contracts that are unable to handle them

## Summary

By not using `_safeMint` for `MeritNFT`, tokens could become stuck in contracts that are unable to handle them.

## Vulnerability Detail

The `mint` function in `MeritNFT` is defined as follows...

```solidity
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```

It is a guarded wrapper around the OZ-defined `_mint`. However, `_mint` is not a safe mint, and so tokens could become stuck in contracts that are unable to handle them.

## Impact

Users who are unaware of the nuances of ERC721 could accidentally have their newly-minted NFTs stuck in contracts that are unable to handle them.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63

## Tool used

Manual Review

## Recommendation

The OZ `_safeMint` function should be used instead of `_mint`.

```diff
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
-       _mint(_receiver, _tokenId);
+       _safeMint(_receiver, _tokenId);
    }
```
