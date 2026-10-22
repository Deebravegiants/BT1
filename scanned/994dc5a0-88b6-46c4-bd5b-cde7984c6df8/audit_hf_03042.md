# [M] safeTransfer is not implemented correctly

## Summary
Severity: Medium
Contest weight: 0.6212
Dataset id: 17064
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The safeTransfer function Safely transfers `tokenId` token from `from` to `to`, checking first that contract recipients are aware of the ERC721 protocol to prevent tokens from being forever locked. But seems like this safety check got missed in the `_safeTransfer` function leading to non secure ERC721 transfers

## Proof of Concept
1. User calls the `safeTransferFrom` function (Using NToken contract which implements MintableIncentivizedERC721 contract)
```solidity
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
```solidity
function _safeTransferFrom(
    address from,
    address to,
    uint256 tokenId,
    bytes memory _data
) internal {
    require(
        _isApprovedOrOwner(_msgSender(), tokenId),
        "ERC721: transfer caller is not owner nor approved"
    );
    _safeTransfer(from, to, tokenId, _data);
}

function _safeTransfer(
        address from,
        address to,
        uint256 tokenId,
        bytes memory
    ) internal virtual {
        _transfer(from, to, tokenId);
    }
```
3. Now lets see `_transfer` function
```solidity
function _transfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual {
        MintableERC721Logic.executeTransfer(
            _ERC721Data,
            POOL,
            ATOMIC_PRICING,
            from,
            to,
            tokenId
        );
    }
```
4. This is calling `MintableERC721Logic.executeTransfer` which simply transfers the asset
5. In this full flow there is no check to see whether `to` address can support ERC721 which fails the purpose of `safeTransferFrom` function
6. Also notice the comment mentions that `data` parameter passed in safeTransferFrom is sent to recipient in call but there is no such transfer of `data`

## Recommendation
Add a call to `onERC721Received` for recipient and see if the recipient actually supports ERC721.

This is by design. We want to avoid re-entrancy to our contracts and so we removed calling the hook.
