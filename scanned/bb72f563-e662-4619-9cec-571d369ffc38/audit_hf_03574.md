# [M] Centralization risk

## Summary
Severity: Medium
Contest weight: 0.0843
Dataset id: 19491
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The protocol has a `DEFAULT_ADMIN_ROLE` with privileged rights to perform admin tasks that can affect users. Especially, the owner can change the fee/reward fraction settings and various policies.

Most admin functions don't emit events at the moment.

** While the protocol owner is regarded as a trusted party, the owner can change many settings and policies without logging. This might lead to unexpected results and users might be affected.

## Recommendation
** Specify the owner's privileges and responsibilities in the documentation.
Add constant state variables that can be used as the minimum and maximum values for the fraction settings.
Log the changes in the important state variables via events.
