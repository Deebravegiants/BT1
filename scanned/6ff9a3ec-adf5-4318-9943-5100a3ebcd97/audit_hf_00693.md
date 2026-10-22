# [M] M-14 | LeveragedTokens Pay Disproportionately Higher Streaming Fees

## Summary
Severity: Medium
Contest weight: 0.1259
Dataset id: 2244
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the LeveragedToken contract, the getStreamingFee(remainingMargin) function is named and documented as if it calculated the streaming fee based on the “remaining margin”. However, rather than passing the contract’s remainingMargin to the _getStreamingFee call, the code calls it with the position’s notionalValue: uint256 streamingFee = _getStreamingFee(transientState.notionalValue); As a result, the leveraged token charges streaming fees on the full leveraged exposure instead of the LeveragedToken position’s margin. A 10x LeveragedToken thus would pay 5 times higher streaming fees than a 2x one that has the same actual collateral. This is at odds with the function’s parameter naming convention, which implies that the fee should be assessed against the margin balance rather than the entire notional.

## Recommendation
Consider calculating the streaming fee as a percentage of the remaining margin instead of the LeveragedToken’s total position notional.
