# [M] (previously M-06)

## Summary
Severity: Medium
Contest weight: 0.0753
Dataset id: 19683
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For an empty phase, both the endingRoundId and startingRoundId will be 0.
And the roundCount should be 0 instead of 1.
https://github.com/equilibria-xyz/perennial-mono/blob/e801b6eecae6ca609597710d2980bd26184a2ef8/packages/perennial-oracle/contracts/types/ChainlinkRegistry.sol#L77-L82
When empty phases are involved, the result of getRoundCount() will be incorrect, and therefore OracleVersion will also be incorrect.

## Recommendation
The case of endingRoundId == 0 should be specially treated, because when a past phase's endingRoundId is 0, it means that it is an empty phase.
Fix confirmed.
