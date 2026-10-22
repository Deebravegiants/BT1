# [M] getBridgeFee() may can't work properly

## Summary
Severity: Medium
Contest weight: 0.5830
Dataset id: 22813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in StargateManager.getBridgeFee() The parameter used is not the same as the actual execution of swap(), resulting in incorrect execution.
We use getBridgeFee() to get the cost of executing swapRouter.swap().
```solidity
function getBridgeFee(OperationParameters calldata opParams) external view override returns (uint256) {
    (uint256 gasToSend, ) = swapRouter.quoteLayerZeroFee(
        uint16(opParams.extraUInts[1]),
        1, // swap function type,
        abi.encode(opParams.extraAddresses[0]), // payload
        "0x", // payload, using abi.encode()
        IStargateRouter.lzTxObj({
            dstGasForCall: 0, // extra gas, if calling smart contract,
            dstNativeAmount: 0, // amount of dust dropped in destination wallet
            dstNativeAddr: abi.encode(opParams.extraAddresses[1]) // destination wallet for dust
        })
    );
    // the message fee is the first value in the tuple.
    return gasToSend;
}
```
The above is different from executing swapRouter.swap() in a couple of ways
1. _toAddress = abi.encode(opParams.extraAddresses[0])
• swap() use abi.encodePacked(recipientAddress); length difference 12
2. payload = “0x”
• swap() use bytes(“ ”) , length difference 2
3. dstNativeAddr: abi.encode(opParams.extraAddresses[1]) , -> extraAddresses[1] unused, may out-of-bounds
getBridgeFee() may revert out-of-bounds can't work properly or returns the wrong fees causing swapRouter.swap() to not work properly

## Recommendation
```solidity
function getBridgeFee(OperationParameters calldata opParams) external view override returns (uint256) {
    (uint256 gasToSend, ) = swapRouter.quoteLayerZeroFee(
        uint16(opParams.extraUInts[1]),
        1, // swap function type,
        abi.encodePacked(opParams.extraAddresses[0]), // payload
        "", // payload, using abi.encode()
        IStargateRouter.lzTxObj({
            dstGasForCall: 0, // extra gas, if calling smart contract,
            dstNativeAmount: 0, // amount of dust dropped in destination wallet
            dstNativeAddr: "0x" // destination wallet for dust
        })
    );
    // the message fee is the first value in the tuple.
    return gasToSend;
}
```
