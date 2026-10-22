# [C] CRT-2 Potential withdrawal lock and invalid distribution

## Summary
Severity: Critical
Contest weight: 0.1935
Dataset id: 2787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
How to reproduce bug:
Deposit N tokens from Alice
Deposit N tokens from Bob
Deposit N tokens from Eve
Send M (relatively huge amount) to Lockup contract directly (via transfer)
Request and withdraw N tokens to Alice
Request and withdraw N tokens to Bob
Request and withdraw N tokens to Eve
At this point participant got different withdrawn amount(first lost more funds), and depending on M amount sometimes contract can be failed on request call
Detailed explanation:
Use particular deflationary token as depositing asset
https://gist.github.com/algys/eb905ec8efa41f80cf1eab57a3b31649
After all withdrawals Alice lost more funds than Eve, that behavior is unfair because they deposited same amount and just lost funds depending on withdrawal order

## Recommendation
It is recommended to fix rebase logic related to lockup balance based calculation
2.2 MAJOR
Not Found
