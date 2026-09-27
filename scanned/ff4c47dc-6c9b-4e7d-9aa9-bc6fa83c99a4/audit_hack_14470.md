# [M] Missing Check for if the `_receiver` is `ERC721` compatible.

## Summary
Severity: Medium
Reporter: 0xdice91
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61C3-L63C6
Type: audit-issue

## Details
# Missing Check for if the `_receiver` is `ERC721` compatible.

## Summary
During minting the `_receiver` address is not checked if it is `ERC721` compatible. If it cannot handle an `ERC721` token, it will be lost forever.
## Vulnerability Detail
In minting, the function `mint` is called by the `Minter`, which then calls the internal `_mint()` function but this function only ensures that the receiver is not address zero. So if the token is minted to an address that can not handle it, it will be lost forever.
```solidity
 file:dutch-nft/src
/MeritNFT.sol
 function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```

```solidity
 file:openzeppelin-contracts/contracts/token/ERC721/ERC721.sol
 function _mint(address to, uint256 tokenId) internal virtual {
        if (to == address(0)) {
            revert ERC721InvalidReceiver(address(0));
        }
// More Code...
 }
```
## Impact
Tokens will be lost forever if minted to a non-compatible address.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61C3-L63C6

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/a55af77c75e8e5ce5205d2787856ee52055adf11/contracts/token/ERC721/ERC721.sol#L272-L275
## Tool used
Manual Review

## Recommendation
The receiver address should be checked if it is ERC721 compatible before minting.
