# [H] PAIR-1 | Duplicate Dividends

## Summary
Severity: High
Contest weight: 0.1328
Dataset id: 4058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the mint function, the only precondition for adding an address to the users list is if the balance of the address is 0. Additionally, an address is not removed from the users list if it transfers it’s balance of the BridgesPair token.
This way an address can continually mint and transfer/burn it’s tokens to enter the users list multiple times. Multiple entries in the users list will result in multiple dividends being paid out in the distributeDividends function.

## Recommendation
Add a check for addresses that are already in the users list.
