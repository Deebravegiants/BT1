# [M] safeTransfer is not implemented correctly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-paraspace
Published: 2022-12-08
Source: https://github.com/code-423n4/2022-11-paraspace-findings/issues/235
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-paraspace/blob/main/paraspace-core/contracts/protocol/tokenization/base/MintableIncentivizedERC721.sol#L320


# Vulnerability details

## Impact
The safeTransfer function Safely transfers `tokenId` token from `from` to `to`, checking first that contract recipients are aware of the ERC721 protocol to prevent tokens from being forever locked. But seems like this safety check got missed in the `_safeTransfer` function leading to non secure ERC721 transfers

## Proof of Concept
1. User calls the `safeTransferFrom` function (Using NToken contract which implements MintableIncentivizedERC721 contract)

```
function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory _data
    ) external virtual override nonReentrant {
        _safeTransferFrom(from, to, tokenId, _data);
    }
```

2. This makes an internal call to _safeTransferFrom -> _safeTransfer -> _transfer

```
function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory _data
    ) external virtual override nonReentrant {
        _safeTransferFrom(from, to, tokenId, _data);
    }

    function _safeTransferFrom(
        address from,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-paraspace-findings/issues/235_
