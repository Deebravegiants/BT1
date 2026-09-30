# [M] Revised Logic in decreasePositionETH()

## Summary
Severity: Medium
Contest weight: 0.4622
Dataset id: 12650
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.6, the FutureRouter contract is a router that facilitates user trading using ETH directly with the protocol. The refund in WETH will be converted to ETH and transferred to the user. While reviewing the refund from the decrease of a WETH position, we notice a possible denial-of-service issue within current implementation.
In the following, we show the related code snippets of the decreasePositionETH()/_decreasePosition() routines. As the name indicates, the decreasePositionETH() routine is used to decrease a WETH position and refund ETH to the position owner. In order to withdraw ETH form WETH, it is expected to withdraw WETH to the current contract ﬁrst. So the _receiver of the _decreasePosition() routine is set to the current contract address, i.e., address(this) (line 498).
However, we notice that in the _decreasePosition() routine, it requires the _receiver must be the position owner, i.e., msg.sender (line 655). As a result, the validation of the _receiver will fail and the transaction reverts. Note the same issue is also applicable to the decreaseMarginETH() routine where the call to the Future::decreaseMargin() routine requires the _receiver must be the position owner.
What's more, in the _decreasePosition() routine, the last parameter, i.e., _tokenOut, gives the desired token the user wants to receive from the position decrease. However, in the _decreasePosition() routine, it uses address(this) (line 499) as the desired token, though the current contract is not a token contract.
```solidity
function decreasePositionETH(
    address _collateralToken,
    address _indexToken,
    bool _isLong,
    uint256 _marginDelta,
    uint256 _notionalDelta,
    uint256 _collateralPrice,
    uint256 _indexPrice,
    address payable _receiver
) external {
    require(_collateralToken == weth, "invalid_collateral");
    uint256 amountOut = _decreasePosition(
        _collateralToken,
        _indexToken,
        _isLong,
        _marginDelta,
        _notionalDelta,
        _collateralPrice,
        _indexPrice,
        address(this),
        address(this)
    );
    IWETH(weth).withdraw(amountOut);
    _receiver.sendValue(amountOut);
}
function _decreasePosition(
    address _collateralToken,
    address _indexToken,
    bool _isLong,
    uint256 _marginDelta,
    uint256 _notionalDelta,
    uint256 _collateralPrice,
    uint256 _indexPrice,
    address _receiver,
    address _tokenOut
) private returns (uint256) {
    require(msg.sender == _receiver, "Invalid caller");
    if (_collateralPrice > 0) {
        require(IFuture(future).getPrice(_collateralToken) >= _collateralPrice, "price_limit");
    }
    if (_indexPrice > 0) {
        require(IFuture(future).getPrice(_indexToken) <= _indexPrice, "price_limit");
    }
    if (address(tradeStakeUpdater) != address(0)) {...}
    if (_tokenOut != _collateralToken) {
        uint256 _amountOut = IFuture(future).decreasePositionByRatio(
            _collateralToken,
            _indexToken,
            msg.sender,
            _isLong,
            _notionalDelta,
            address(this)
        );
        IERC20(_collateralToken).approve(swapPool, _amountOut);
        return ISwapForFuture(swapPool).swapIn(
            _collateralToken,
            _tokenOut,
            _amountOut,
            _receiver,
        );
    }
```

## Recommendation
Revise the decreasePositionETH()/decreaseMarginETH() routines and ensure they can receive WETH into the FutureRouter contract and a valid desired token address can be provided to the _decreasePosition() routine.
