# [M] In the function _handleERC20Received, the

## Summary
Severity: Medium
Contest weight: 0.5611
Dataset id: 22598
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the function _handleERC20Received, the fee was incorrectly charged. In the contract, when external swap occurs, a portion of the fee will be charged. However, in function _handleERC20Received, the fee is also charged in internal swap.
```solidity
} else {
// Deduct the external swap fee
uint256 fee = (bridgedAmount * dstExternalFeeRate) / FEE_BASE;
bridgedAmount -= fee;
TransferHelper.safeApprove(bridgedToken, address(wooRouter), bridgedAmount);
if (dst1inch.swapRouter != address(0)) {
try
wooRouter.externalSwap(
```
At the same time, when the internal swap fails, this part of the fee will not be returned to the user. Internal swaps are incorrectly charged, and fees are not refunded when internal swap fail.

## Recommendation
Apply fee calculation only to external swaps.
```solidity
function _handleERC20Received(
uint256 refId,
address to,
address toToken,
address bridgedToken,
uint256 bridgedAmount,
uint256 minToAmount,
Dst1inch memory dst1inch
) internal {
address msgSender = _msgSender();
} else {
if (dst1inch.swapRouter != address(0)) {
// Deduct the external swap fee
uint256 fee = (bridgedAmount * dstExternalFeeRate) / FEE_BASE;
bridgedAmount -= fee;
TransferHelper.safeApprove(bridgedToken, address(wooRouter), bridgedAmount);
try
wooRouter.externalSwap(
)
returns (uint256 realToAmount) {
emit WooCrossSwapOnDstChain(
);
} catch {
bridgedAmount += fee;
TransferHelper.safeTransfer(bridgedToken, to, bridgedAmount);
emit WooCrossSwapOnDstChain(
);
}
} else {
TransferHelper.safeApprove(bridgedToken, address(wooRouter), bridgedAmount);
try wooRouter.swap(bridgedToken, toToken, bridgedAmount, minToAmount, payable(to), to) returns (
uint256 realToAmount
) {
} catch {
}
}
}
}
```
