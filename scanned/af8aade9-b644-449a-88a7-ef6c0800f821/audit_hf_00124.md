# [M] Transfer fee avoidance

## Summary
Severity: Medium
Contest weight: 0.0533
Dataset id: 333
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `Vether4.addExcluded()` function on mainnet (0x4Ba6dDd7b89ed838FEd25d208D4f644106E34279) allows a user to exclude an address from transfer fees for a cost of 128 VETH. By exploiting the conditions in which fees are taken, it is possible to set up a contract for a once-off cost in which all users can use to avoid transfer fees.

## Recommendation
No recommendation
