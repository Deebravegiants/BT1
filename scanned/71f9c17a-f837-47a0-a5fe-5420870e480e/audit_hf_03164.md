# [M] Loan duration can exceed the end of the next

## Summary
Severity: Medium
Contest weight: 0.0894
Dataset id: 17724
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
epoch
Loan duration can exceed the end of the next epoch, which deviates from the protocol specification. From the specs: "The duration of new loans is restricted to not exceed the end of the next epoch. For example, if a PublicVault is 15 days into a 30-day epoch, new loans must not be longer than 45 days." However, there's no enforcement of this requirement. The implementation does not adhere to the spec: Loan duration can exceed the end of the next epoch, which breaks protocol specification and therefore lead to miscalculations and potential fund loss.

## Recommendation
Implement as per specification or revisit the specification.
