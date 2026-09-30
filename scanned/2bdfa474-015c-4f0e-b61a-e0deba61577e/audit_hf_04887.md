# [M] Users are heavily overcharged for gas fees if

## Summary
Severity: Medium
Contest weight: 0.4273
Dataset id: 22803
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users are heavily overcharged for gas fees if they're bridging ETH. In Messi, the amount of gas we charge fees on is the gas used for claim and swap operations plus valueToSend (the ETH to bridge, not including the bridging fee, so this will only be non-zero if we're bridging with ETH).
```solidity
(gasCharged, gasAmountCharged) = tryToChargeForGas(
    (initialGas - gasleft()) * tx.gasprice + valueToSend, <-- gasAmount
    gasToFeeTokenExchangeRate,
    feesTokenAddress,
    receivingUser,
    true,
    gasCharged,
    bridgeFound? bridgeOp.inputToken != feesTokenAddress: swapOps.length > 0? swapOps[swapOps.length - 1].outputToken != feesTokenAddress: claimOp.outputToken != feesTokenAddress
);
```
We directly calculate the fee amount to be paid using the uint256 feeValue = (gasAmount * gasToFeeTokenExchangeRate) / 10 ** 18; Since gasAmount includes valueToSend, if we're bridging with ETH (e.g. using StargateManager), we will have to pay fees for gas + the full value of the amount we're bridging. When the fee token is not ETH, the fee amount will be transferred from the receivingUser to feeCollector which is not unlikely since the receivingUser could have approved a large amount (or even max amount) to the Messi contract for convenience. Loss of funds for users due to heavily overpriced gas fees when bridging ETH.

## Recommendation
Replace valueToSend in the gasAmount parameter with ‘bridgeFeeEth' (which is provided by the caller, not the receiving user) when charging for gas.
