# [M] Swap will unnecessarily revert in some cases

## Summary
Severity: Medium
Contest weight: 0.3994
Dataset id: 22812
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Swap will unnecessarily revert in some cases if initial ETH -> token swap is split into multiple swapOps
In the case where fee is charged in ETH, it is charger before the swapOps. The problem is that the swap eth -> token could be split into multiple swapOps (e.g. due to using different exchanges for better prices). However, the fee is always attempted to be deducted from the first swapOps. In the case where the first swapOp is of less value, it may cause a revert due to underflow.
```solidity
(succeeded, feesCharged) = tryToChargeFees(
    feesTokenAddress,
    computableFeeAmount,
    feeRateBps,
    feeReceiver,
    receivingUser,
    false,
    false
);
if (succeeded) {
    if (swapOps.length > 0) {
        require(swapOps[0].amountIn > feesCharged, "Maradona: cannot substract fee from input swap");
    }
}
```
to be deducted from the first swapOp
DoS

## Recommendation
Charge the fees from multiple swapOps if necessary
