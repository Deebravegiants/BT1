# [M] TREC-2 | Invalid Assumption

## Summary
Severity: Medium
Contest weight: 0.0621
Dataset id: 9328
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the acceptTransfer function it is assumed that A maximum of ~7% amount of GMX (as esGMX) would be added, however that assumption does not hold in several cases. A user could have removed their sGMX and only been left with esGMX and bnGMX or a user may have accepted a transfer from another account which perturbed this ratio.

## Recommendation
Do not rely on this assumption holding and remove the comment. If it is paramount that only a small percentage of esGMX is added, add an explicit check.
