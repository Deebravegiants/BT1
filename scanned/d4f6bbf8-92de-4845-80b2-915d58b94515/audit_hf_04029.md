# [M] Multiple functions may leave excess funds in contract

## Summary
Severity: Medium
Contest weight: 0.1482
Dataset id: 20453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Periphery#combine may leave excess underlying in the contract due to _fromTarget
unwrapping to underlying and the quote may not swap them all.
When using arbitrary tokens to swap to underlying the contract always moves in
the full amount specified. There is no guarantee that the quote will consume all
tokens. As a result the contract may leave excess sell tokens in the contract but it
should return then to the receiver.
These functions include:
RollerPeriphery
1) deposit
Periphery
1) swapForPTs
2) addLiquidity
3) issue
RollerPeriphery#RollermintFromUnderlying uses adapter.scale and previewMint to
determine the amount of underlying to transfer. The roller code will mean that
previewMint will always perfectly reflect the exact exchange rate into the roller.
However adapter.scale varies by adapter and isn't guaranteed to be exact. The
result is that _transferFrom may take too much underlying. Since this underlying is
wrapped to target the contract should return all excess target to receiver.
See summary.
Token may be left in the contract and lost

## Recommendation
Return excess tokens at the end of the function
