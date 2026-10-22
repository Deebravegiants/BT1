# [M] Use of transfer instead of safeTransfer in `_redeem()`

## Summary
Severity: Medium
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L129
Type: audit-issue

## Details
# Use of transfer instead of safeTransfer in `_redeem()`

## Summary

Use OpenZeppelin's safeTransfer instead of transfer when transferring ERC20 token.

## Vulnerability Detail

It is recommended to always use safeTransfer when transferring ERC20s, or in our case ERC4626 which is an extension of ERC20. Some ERC20 implementations do not implement a return value such as BNB. This will cause the token to always revert when trying to redeem. 

## Impact

In this case, while it is unlikely for it to happen as Vault token is our own implementation, it is still better to err on the side of caution.

## Code Snippet
[QueueInternal.sol#L129](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L129)
```solidity
    function _redeem(
        uint256 tokenId,
        address receiver,
        address owner
    ) internal {
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();

        // claim tokens cannot be redeemed within the same epoch that they were minted
        require(
            tokenId != currentTokenId,
            "current claim token cannot be redeemed"
        );

        uint256 balance = _balanceOf(owner, tokenId);
        uint256 unredeemedShares = _previewUnredeemed(tokenId, owner);

        // burns claim tokens held by owner
        _burn(owner, tokenId, balance);
        // transfers unredeemed share amount to the receiver
        require(Vault.transfer(receiver, unredeemedShares), "transfer failed");

        uint64 epoch = QueueStorage._getEpoch();
        emit Redeem(epoch, receiver, owner, unredeemedShares);
    }
```

## Tool used

Manual Review

## Recommendation

```diff
- require(Vault.transfer(receiver, unredeemedShares), "transfer failed");
+ Vault.safeTransfer(receiver, unredeemedShares));
```
