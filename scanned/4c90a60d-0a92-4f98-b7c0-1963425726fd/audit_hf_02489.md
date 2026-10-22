# [C] Improved Logic of openPositionViaSignature()

## Summary
Severity: Critical
Contest weight: 0.7704
Dataset id: 13320
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function openPositionViaSignature(
    OpenPositionOrder calldata order_,
    UpdateData[] calldata updateData_,
    address maker_,
    bytes calldata signature_
) external onlyActiveTradePair(order_.params.tradePair) returns (uint256) {
    _updateContracts(updateData_);
    _processSignature(order_, maker_, signature_);
    _verifyConstraints(
        order_.params.tradePair,
        order_.constraints,
        order_.params.isShort ? UsePrice.MAX : UsePrice.MIN
    );
    uint256 positionId = _openPosition(order_.params);
    sigHashToTradeId[keccak256(signature_)] = TradeId(order_.params.tradePair, uint96(positionId));
    emit OpenedPositionViaSignature(order_.params.tradePair, positionId, signature_);
    return positionId;
}
```
```solidity
function _openPosition(OpenPositionParams memory params_) internal returns (uint256) {
    ITradePair(params_.tradePair).collateral().safeTransferFrom(
        msg.sender,
        address(params_.tradePair),
        params_.margin
    );
    userManager.setUserReferrer(msg.sender, params_.referrer);
    uint256 id = ITradePair(params_.tradePair).openPosition(
        msg.sender,
        params_.margin,
        params_.leverage,
        params_.isShort,
        params_.whitelabelAddress
    );
    emit PositionOpened(params_.tradePair, id);
    return id;
}
```
It comes to our attention that the _processSignature() routine validates the order signed by the maker. However, the _openPosition() routine does not take funds from the maker. Instead, it transfers funds from the msg.sender, which will not work as expected.

## Recommendation
Revise the related routines to transfer funds from maker rather than msg.sender.
