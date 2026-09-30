# [H] Block finalization is immediate and permissionless

## Summary
Severity: High
Contest weight: 0.1024
Dataset id: 5657
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Once a block is proposed by the operator, which might malicious e.g. containing a specifically crafted withdrawal root, anyone can immediately invoke the finalize_block instruction to finalize it. Consequently, a malicious withdrawal can be performed immediately after proposing such a block.

## Recommendation
It is recommended to introduce a challenge as well as a validity-proof mechanism that allows validators to challenge a block and prove its validity before it can be finalized.
