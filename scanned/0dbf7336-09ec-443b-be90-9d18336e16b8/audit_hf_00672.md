# [H] H-03 | Extend Interest Stolen

## Summary
Severity: High
Contest weight: 0.1443
Dataset id: 2208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Interest accrued from the extend function sits in the CreditFacility contract until the fee recipient removes it with their approval. However this poses an issue because the _swapExactOut function transfers the entire contract balance of the CreditFacility to the BPOOL contract. As a result these fee amounts which are sitting in the CreditFacility contract will be deployed into the protocol liquidity instead of collectable.

## Recommendation
In the extend function, instead of transferring the reserve amount from the user to the CreditFacility contract, transfer the reserve amount to the fee recipient directly. Furthermore, be sure there are no other instances where reserves are left in the CreditFacility contract.
