# [M] `exitPositionAndRemoveCollateral()` will fail as `MagnetarV2` does not implement `onERC721Received()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1405
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L532-L537


# Vulnerability details


`MagnetarV2` is missing `onERC721Received()` implementation and this will cause `exitPositionAndRemoveCollateral()` to fail when owner of `oTAPTokenID` is `user`.

That is because in in that scenario, `MagnetarV2` will need to transfer in the `oTAP` NFT using `safeTransferFrom()`, which will verify that the recipient implements `onERC721Received()`.

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L532-L537

```Solidity
    function _exitPositionAndRemoveCollateral(
            ...
            if (ownerOfTapTokenId == user) {
                IERC721(oTapAddress).safeTransferFrom(
                    user,
                    address(this),
                    removeAndRepayData.exitData.oTAPTokenID,
                    "0x"
                );
            }
```

## Impact
 `exitPositionAndRemoveCollateral()` will fail when `ownerOfTapTokenId == user`, where the oTAP token is require to be transfered to `MagnetarV2`.


## Recommended Mitigation Steps
Implement `onERC721Received()` in `MagnetarV2`.


## Assessed type

DoS
