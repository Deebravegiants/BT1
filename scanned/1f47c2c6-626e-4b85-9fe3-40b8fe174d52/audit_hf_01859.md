# [M] M-14 Too flexible logic

## Summary
Severity: Medium
Contest weight: 0.0675
Dataset id: 10360
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
updatePolicy can be used to update existing policies or add new ones. The chosen architecture is too flexible, making it harder to control the correctness of parameter updates for the owner. The same issue also applies to the updateMethodCooldown function: • borgCore.sol#L257-L267 • borgCore.sol#L383-L395.

## Recommendation
We recommend updating the current architecture so that there are two different methods: one to add a new policy/cooldown, which checks that the policy/cooldown didn't previously exist, and the second, which allows updating policy/cooldown with checks that such an element was previously added.
