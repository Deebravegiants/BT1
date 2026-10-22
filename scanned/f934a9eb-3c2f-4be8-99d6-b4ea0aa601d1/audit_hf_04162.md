# [M] `TapiocaOptionBroker.participate

## Summary
Severity: Medium
Contest weight: 0.5763
Dataset id: 20792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the user `isApproved()`, the user can call `TapiocaOptionBroker.participate()`. The code is as follows:
```solidity
function participate(uint256 _tOLPTokenID) external whenNotPaused nonReentrant returns (uint256 oTAPTokenID) {
    ...
    TWAMLPool memory pool = twAML[lock.sglAssetID];
    if (pool.cumulative == 0) {
        pool.cumulative = EPOCH_DURATION;
    }

    if (!tOLP.isApprovedOrOwner(msg.sender, _tOLPTokenID)) {
        revert NotAuthorized();
    }

    {
        bool isErr = pearlmit.transferFromERC721(msg.sender, address(this), address(tOLP), _tOLPTokenID);
        if (isErr) revert TransferFailed();
    }
```
However, in the current implementation, even though `msg.sender` has obtained authorization (`isApprovedOrOwner(msg.sender) == true`), it is still unable to execute due to the incorrect usage of: `pearlmit.transferFromERC721(msg.sender, address(this), address(tOLP), _tOLPTokenID);` Passing `msg.sender` as the `owner` will result in failure to execute.

`pearlmit.transferFromERC721(msg.sender,to)` -> `IERC721(token).transferFrom(owner, to)` -> `_transfer(owner,to)` -> `require(ERC721.ownerOf(tokenId) == owner`.

It will check the first parameter is the owner of NFT. It should use: `pearlmit.transferFromERC721(tOLP.ownerOf(_tOLPTokenID), address(this), address(tOLP), _tOLPTokenID)`.

## Recommendation
```solidity
function participate(uint256 _tOLPTokenID) external whenNotPaused nonReentrant returns (uint256 oTAPTokenID) {
    ...
    if (!tOLP.isApprovedOrOwner(msg.sender, _tOLPTokenID)) {
        revert NotAuthorized();
    }

    // Transfer tOLP position to this contract
    // tOLP.transferFrom(msg.sender, address(this), _tOLPTokenID);
    {
        bool isErr = pearlmit.transferFromERC721(tOLP.ownerOf(_tOLPTokenID), address(this), address(tOLP), _tOLPTokenID); 
        if (isErr) revert TransferFailed();
    }
```
