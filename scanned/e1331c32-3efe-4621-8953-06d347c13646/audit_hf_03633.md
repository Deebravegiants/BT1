# [M] GMXFuturePoolHedger does not implement

## Summary
Severity: Medium
Contest weight: 0.6911
Dataset id: 19702
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMXFuturePoolHedger does not implement receive fallback function to receive the
execution fee refund when increase position and decrease position are canceled
When increase or decrease position, the execution fee is sent to the PositionRouter
contract.
```solidity
uint executionFee = _getExecutionFee();
bytes32 key = positionRouter.createIncreasePosition{value: executionFee}(
    path,
    address(baseAsset), // index token
    collateralDelta, // amount in via router is in the native currency decimals
    0, // min out
    _convertToGMXPrecision(sizeDelta),
    isLong,
    acceptableSpot,
    executionFee,
    referralCode,
    address(0)
);
```
and
```solidity
uint executionFee = _getExecutionFee();
bytes32 key = positionRouter.createDecreasePosition{value: executionFee}(
    path,
    address(baseAsset),
    // CollateralDelta for decreases is in PRICE_PRECISION rather than asset
    decimals like for opens...
    // In the case of closes, 0 must be passed in
    isClose ? 0 : _convertToGMXPrecision(collateralDelta),
    _convertToGMXPrecision(sizeDelta),
    isLong,
    address(liquidityPool),
    acceptableSpot,
    0,
    executionFee,
    false,
    address(0)
);
```
According to the GMX doc,
https://gmx-io.notion.site/gmx-io/GMX-Technical-Overview-47fc5ed832e243afb9
e97e8a4a036353
The PositionRouter contract handles a two part transaction process for increasing
or decreasing long / short positions, this process helps to reduce front-running
issues:
1. A user sends the request to increase / decrease a position to the
PositionRouter
2. A keeper requests the index price
3. The keeper then executes the position at the current index price
4. If the position cannot be executed within the allowed slippage the request is
cancelled and the funds are sent back the user
If the position cannot be executed within the allowed slippage the request is
cancelled and the funds are sent back the user
When the request is canceled, the execution fee is supposed to be refunded to the
GMXFuturePoolHedger
```solidity
/**
* @dev cancel outstanding order in case the GMX keeper bot is not working
properly.
*/
function cancelPendingOrder() external nonReentrant {
    if (lastOrderTimestamp + futuresPoolHedgerParams.minCancelDelay > block.timestamp)
        revert CancellationDelayNotPassed();
    if (_hasPendingIncrease()) {
        bool success = positionRouter.cancelIncreasePosition(pendingOrderKey, address(this));
        emit OrderCanceled(pendingOrderKey, success);
    }
    if (_hasPendingDecrease()) {
        bool success = positionRouter.cancelDecreasePosition(pendingOrderKey, address(this));
        emit OrderCanceled(pendingOrderKey, success);
    }
    pendingOrderKey = bytes32(0);
}
```
the code above pass in address(this) as the executionFeeReceiver
Now we look into the code on GMX side
https://github.com/gmx-io/gmx-contracts/blob/d5ad12288a79c672ad7553bd772c
09bfca231c11/contracts/core/PositionRouter.sol#L459
```solidity
function cancelIncreasePosition(bytes32 _key, address payable _executionFeeReceiver) public nonReentrant returns (bool) {
    IncreasePositionRequest memory request = increasePositionRequests[_key];
    // if the request was already executed or cancelled, return true so that the
    executeIncreasePositions loop will continue executing the next request
    if (request.account == address(0)) { return true; }
    bool shouldCancel = _validateCancellation(request.blockNumber, request.blockTime, request.account);
    if (!shouldCancel) { return false; }
    delete increasePositionRequests[_key];
    if (request.hasCollateralInETH) {
        _transferOutETHWithGasLimitIgnoreFail(request.amountIn, payable(request.account));
    } else {
        IERC20(request.path[0]).safeTransfer(request.account, request.amountIn);
    }
    _transferOutETHWithGasLimitIgnoreFail(request.executionFee, _executionFeeReceiver);
    emit CancelIncreasePosition(
        request.account,
        request.path,
        request.indexToken,
        request.amountIn,
        request.minOut,
        request.sizeDelta,
        request.isLong,
        request.acceptablePrice,
        request.executionFee,
        block.number.sub(request.blockNumber),
        block.timestamp.sub(request.blockTime)
    );
    _callRequestCallback(request.callbackTarget, _key, false, true);
    return true;
}
_transferOutETHWithGasLimitIgnoreFail(request.executionFee, _executionFeeReceiver);
```
Which calls:
https://github.com/gmx-io/gmx-contracts/blob/d5ad12288a79c672ad7553bd772c
09bfca231c11/contracts/core/BasePositionManager.sol#L279
```solidity
function _transferOutETHWithGasLimitIgnoreFail(uint256 _amountOut, address payable _receiver) internal {
    IWETH(weth).withdraw(_amountOut);
    // use `send` instead of `transfer` to not revert whole transaction in case
    ETH transfer was failed
    // it has limit of 2300 gas
    // this is to avoid front-running
    _receiver.send(_amountOut);
}
```
sure the failure on execution fee refunding will be block the cancel.
Then cancel request from cancelPendingOrder in GMXFuturePoolHedger may go
through, but because the GMXFuturePoolHedger does not implement the receive
fallback function, the execution fee refund fail sliently and the executee fee is lost
even though the request is canceled.
the execution fee refund fail sliently and the executee fee is lost even though the
request is canceled.

## Recommendation
We recommend the project implement receive fallback in GMXFuturePoolHedger to
make sure the execution fee is received properly.
```solidity
receive() external payable {
}
```
