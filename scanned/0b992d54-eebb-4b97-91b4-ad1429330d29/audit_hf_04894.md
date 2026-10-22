# [M] minAmountOut check must be done after charg-

## Summary
Severity: Medium
Contest weight: 0.5515
Dataset id: 22810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
minAmountOut check must be done after charging the fees
Currently, in case the fees are charged from the last output token, first the minAmountOut check is done and then the fees are deducted.
```solidity
require(lastOutBalance - prevLastOutBalance >= minAmountOut, "Maradona: last output amount is less than minAmountOut");
```
// End of (2)
// (3) We try again to charge fees
```solidity
if (!succeeded) {
    (succeeded, ) = tryToChargeFees(
        feesTokenAddress,
        lastOutBalance,
        feeRateBps,
        feeReceiver,
        receivingUser,
        true,
        succeeded
    );
}
```
This would cause users to receive less funds than what they've said as minAmountOut and ultimately break a core invariant.
taken from ETH (input token), everything works as expected.
Users receiving less than the minimum they've specified

## Recommendation
put the minAmountOut check after charging the fees
