# [M] DoS attack if assets are transferred before a fundLoan() call.

## Summary
Severity: Medium
Contest weight: 0.0482
Dataset id: 10241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In fixed term loans, a DoS attack is possible if assets are transferred into the MapleLoan before the loan is funded. Exploit scenario ● delegate funds loan ● attacker frontruns delegate and transfers fundsAsset to the MapleLoan ● funding reverts due to the require that the unaccounted funds are 0

## Recommendation
Skim before funding.
