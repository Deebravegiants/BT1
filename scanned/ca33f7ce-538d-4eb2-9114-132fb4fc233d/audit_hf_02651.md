# [M] Limitations of Exposure Ceiling

## Summary
Severity: Medium
Contest weight: 0.0879
Dataset id: 14372
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An exposure ceiling was intended to be added as a control a) against supply attacks such as infinite minting which would allow draining of all funds in the pool and b) disabling an asset to be used as collateral on new loans. The exposure ceiling would reduce the Loan to Value (LTV) ratio of an asset to zero once the total supply of an asset breached the exposure cap without reducing the ability of this asset to be used as collateral for existing loans (through the liquidation threshold).

## Recommendation
It was deemed infeasible to implement the exposure cap solving both issues mentioned above without enforcing strict conditions which significantly reduce the user experience and increase gas cost.
