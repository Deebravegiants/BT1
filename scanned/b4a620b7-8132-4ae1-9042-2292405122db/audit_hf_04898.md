# [M] StargateManager.bridge() when isFromEth ,

## Summary
Severity: Medium
Contest weight: 0.6935
Dataset id: 22814
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in StargateManager.bridge() when isFromEth , miss check outputToken The user can arbitrarily specify feesTokenAddress == bridgeOp.outputToken == MockToken(valueless) to avoid fees
in validateFeeToken() The user-specified feesTokenAddress can be either ops[0].inputToken or bridgeOp.outputToken So we need to check the validity of bridgeOp.outputToken Example: CCTPManager.bridge()
```solidity
function bridge(OperationParameters calldata opParams) external payable override {
    ...
    require(destination != 0, "CCTPManager: invalid destination");
    address tokenAddress = opParams.inputToken;
    require(tokenAddress != address(0), "CCTPManager: invalid token address");
    require(opParams.outputToken == address(0), "CCTPManager: invalid output token");
}
```
StargateManager.bridge() check the following
```solidity
function bridge(OperationParameters calldata opParams) external payable override {
    bool isFromEth = opParams.inputToken == address(0);
    uint16 destination = uint16(opParams.extraUInts[1]);
    require(destination != 0, "StargateManager: invalid destination");
    uint256 operation = opParams.extraUInts[0];
    require(operation == uint256(BridgeLib.OperationType.BRIDGE), "StargateManager: only bridge is allowed");
    address payable refundAddress = payable(address(this));
    address recipientAddress = opParams.extraAddresses[0];
    require(recipientAddress != address(0), "StargateManager: invalid recipient address");
    bytes memory to = abi.encodePacked(recipientAddress);
    require(to.length > 0, "StargateManager: invalid to address");
    uint256 amountIn = opParams.amountIn;
    require(amountIn > 0, "StargateManager: invalid amount");
    uint256 minAmountOut = opParams.minAmountOut;
    require(minAmountOut > 0, "StargateManager: invalid min amount out");
    if (isFromEth) {
        swapRouterETH.swapETH{ value: msg.value }(destination, refundAddress, to, amountIn, minAmountOut);
    } else {
        address tokenAddress = opParams.inputToken;
        require(tokenAddress != address(0), "StargateManager: invalid token address");
        require(opParams.outputToken == tokenAddress, "StargateManager: invalid output token");
        ...
    }
```
From the code above we know that If isFromEth=true doesn't check the outputToken, the user can specify any useless token to pay the fee.
Malicious fee evasion

## Recommendation
```solidity
function bridge(OperationParameters calldata opParams) external payable override {
    bool isFromEth = opParams.inputToken == address(0);
    ...
    if (isFromEth) {
        require(opParams.outputToken == address(0), "StargateManager: invalid output token");
        swapRouterETH.swapETH{ value: msg.value }(destination, refundAddress, to, amountIn, minAmountOut);
    } else {
```
