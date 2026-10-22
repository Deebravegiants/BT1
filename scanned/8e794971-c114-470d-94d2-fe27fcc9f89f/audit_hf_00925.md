# [C] CRT-1 Unfair withdrawn amount

## Summary
Severity: Critical
Contest weight: 0.1619
Dataset id: 2786
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
How to reproduce bug:
Deposit N tokens from Alice
Deposit N tokens from Bob
Deposit N tokens from Eve
Request and withdraw N tokens to Alice
Request and withdraw N tokens to Bob
Request and withdraw N tokens to Eve
At this point participant got different withdrawn amount(first lost more funds)
Detailed explanation:
Use particular deflationary token as depositing asset
https://gist.github.com/algys/eb905ec8efa41f80cf1eab57a3b31649
After all withdrawals Alice lost more funds than Eve, that behavior is unfair because they deposited same amount and just lost funds depending on withdrawal order

## Recommendation
It is recommended to refactor rebase logic and reduce amount of code duplication.
