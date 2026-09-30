# [M] VLT-6 | Attacker can Front-Run Removal of Asset

## Summary
Severity: Medium
Contest weight: 0.1217
Dataset id: 20593
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an LST is removed with the removeLst function, the value of that LST in the system will no longer be attributed to the totalAssets. Therefore a malicious actor may frontrun the removal of an LST and deposit that exact LST into the system before withdrawing that value in a different LST token, as a result the value of restEth will drop and holders will immediately lose the value of the removed LST tokens in the system. If the protocol were to add the removed LST back it would create a positive stepwise jump in the value of restEth. This way an attacker could game the stepwise jump by depositing before the LST is added back and withdrawing afterwards for an immediate profit.

## Recommendation
Introduce a mechanism for deposits of a certain LST to be paused, or deposits as a whole to be paused. Additionally, consider implementing validation that an LST cannot be removed unless the vault holds no value in the corresponding strategy and no balance of that LST directly in the vault contract. This prevents unlisted tokens from being lost to depositors.
