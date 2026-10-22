# [M] WooCrossChainRouterV4.crossSwap()doesn't cor-

## Summary
Severity: Medium
Contest weight: 0.7008
Dataset id: 22596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
WooCrossChainRouterV4.crossSwap() doesn't correctly check for slippage, as it deducts external swapping fees after checking for the minimum bridged amount determined by the user.
• WooCrossChainRouterV4.crossSwap() function is meant to enable users from executing a cross-chain swap, where a cross chain swap transaction may include all or some of the following steps (as per the documentation):
1. Swap asset A in the user's wallet to asset B in WOOFi on the source chain
2. Then bridging asset B to asset C on the destination chain via Stargate (asset B and asset C are of the same value)
3. Then swap asset C to asset D in WOOFi on the destination chain and send to the wallet instructed by the user.
• So swapping from asset A to asset B on the source chain can be done either using a woofi pool (WooPPV2) via wooRouter.swap(), or this swap can be done via an external aggregater (where 1inch aggregator is going to be used) via wooRouter.externalSwap() that redirects the swap call to the external aggregator:
```solidity
// Step 2: local swap by 1inch router
if (srcInfos.fromToken != srcInfos.bridgeToken) {
TransferHelper.safeApprove(srcInfos.fromToken, address(wooRouter), srcInfos.fromAmount);
if (src1inch.swapRouter != address(0)) {
// external swap via 1inch
bridgeAmount = wooRouter.externalSwap(
src1inch.swapRouter,
src1inch.swapRouter,
srcInfos.fromToken,
srcInfos.bridgeToken,
srcInfos.fromAmount,
srcInfos.minBridgeAmount,
payable(address(this)),
src1inch.data
);
fee = (bridgeAmount * srcExternalFeeRate) / FEE_BASE;
} else {
//some code...
}
// Step 3: deduct the swap fee
bridgeAmount -= fee;
```
where the resulted bridgeAmount will be checked to be > srcInfos.minBridgeAmount in the wooRouter.externalSwap():
```solidity
function externalSwap(
address approveTarget,
address swapTarget,
address fromToken,
address toToken,
uint256 fromAmount,
uint256 minToAmount,
address payable to,
bytes calldata data
) external payable override nonReentrant returns (uint256 realToAmount)
{
//some code...
require(realToAmount >= minToAmount && realToAmount > 0, "WooRouter: realToAmount_NOT_ENOUGH");
//some code...
}
```
But as can be noticed, an external swap fee is deducted from the bridgeAmount after the swap is done via an external aggregator (1inch aggregator) and after checking that the bridgeAmount is sufficient as per detrmined by the user ( > srcInfos.minBridgeAmount), and this might result in the bridgeAmount being less than required by the user srcInfos.minBridgeAmount. WooCrossChainRouterV4.crossSwap function/L137-L138
```solidity
// Step 2: local swap by 1inch router
if (srcInfos.fromToken != srcInfos.bridgeToken) {
TransferHelper.safeApprove(srcInfos.fromToken, address(wooRouter), srcInfos.fromAmount);
if (src1inch.swapRouter != address(0)) {
// external swap via 1inch
bridgeAmount = wooRouter.externalSwap(
src1inch.swapRouter,
src1inch.swapRouter,
srcInfos.fromToken,
srcInfos.bridgeToken,
srcInfos.fromAmount,
srcInfos.minBridgeAmount,
payable(address(this)),
src1inch.data
);
fee = (bridgeAmount * srcExternalFeeRate) / FEE_BASE;
} else {
//some code...
}
// Step 3: deduct the swap fee
bridgeAmount -= fee;
```

## Recommendation
Update WooCrossChainRouterV4.crossSwap() to check for the bridgeAmount being greater than the amount determined by the user srcInfos.minBridgeAmount after deducting the fees:
```solidity
function crossSwap(
uint256 refId,
address payable to,
SrcInfos memory srcInfos,
DstInfos calldata dstInfos,
Src1inch calldata src1inch,
Dst1inch calldata dst1inch
) external payable whenNotPaused nonReentrant {
//some code...
// Step 2: local swap by 1inch router
if (srcInfos.fromToken != srcInfos.bridgeToken) {
TransferHelper.safeApprove(srcInfos.fromToken, address(wooRouter), srcInfos.fromAmount);
if (src1inch.swapRouter != address(0)) {
// external swap via 1inch
bridgeAmount = wooRouter.externalSwap(
src1inch.swapRouter,
src1inch.swapRouter,
srcInfos.fromToken,
srcInfos.bridgeToken,
srcInfos.fromAmount,
srcInfos.minBridgeAmount,
payable(address(this)),
src1inch.data
);
fee = (bridgeAmount * srcExternalFeeRate) / FEE_BASE;
} else {
//some code...
}
// Step 3: deduct the swap fee
bridgeAmount -= fee;
require(bridgeAmount >= srcInfos.minBridgeAmount, "insufficient bridged amount");
//some code...
```
