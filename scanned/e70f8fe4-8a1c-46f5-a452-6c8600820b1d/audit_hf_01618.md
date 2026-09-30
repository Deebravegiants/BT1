# [M] Wrong accounting for rebase/fee-on-transfer tokens

## Summary
Severity: Medium
Contest weight: 0.0947
Dataset id: 8724
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, anyone can add any tokens from the CurrencyList contract. This means that rebase and fee-on-transfer tokens can be added intentionally or by mistake which will cause errors in the accounting of the balances of such tokens. Rebasing tokens are designed to adjust the supply of tokens automatically based on the market demand while fee-on-transfer tokens charge a fee on each transfer. This would lead to having less tokens than expected in the contract and the accounting of such tokens will be completely wrong.

## Recommendation
Consider checking the balance of the contract before and after token transfers and using it instead of the amount specified in the contract. Another possible solution is to add access control and allow only specific roles to call addCurrencyToList.
