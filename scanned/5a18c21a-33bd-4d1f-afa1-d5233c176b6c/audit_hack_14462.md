# [M] Useers may lose their NFts

## Summary
Severity: Medium
Reporter: mahyar
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61
Type: audit-issue

## Details
# Useers may lose their NFts

## Summary
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61

If caller is contract that doesn't support ERC721 the minted NFT will be locked in the contract.

## Vulnerability Detail

In `MeritDutchAuction.sol` contract users can call `mint` function with some value sent to buy NFTs and the function calls `mint` function in `MeritNFT`, but if the caller is contract that cannot handle ERC721 token the minted token will be **lost** in the contract.
[EIP-721 documentation also mentioned](https://eips.ethereum.org/EIPS/eip-721) :
> A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.


## Impact

Users may lose their NFTs.

## Code Snippet
`MeritNFT.sol::mint` : 
```solidity
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```

## Tool used

Manual Review

## Recommendation

Use `safeMint` insted of `mint` function, here is how it should look like:
```diff
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
-        _mint(_receiver, _tokenId);
+        _safeMint(_receiver,_tokenId);
    }
```
