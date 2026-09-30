# [M] UF-3 | Random Manipulation

## Summary
Severity: Medium
Contest weight: 0.0511
Dataset id: 16217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The random function relies on weak sources of pseudo-randomness from only on-chain attributes. A validator node can manipulate the block.timestamp and therefore the random number. Therefore, the _sendTo address can be manipulated in favor of the validator.

## Recommendation
Utilize the Randomness pattern to obtain on-chain randomness and avoid validator manipulation or obtain random numbers off-chain through an oracle.
