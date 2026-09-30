# [C] C-09 | Traders Proﬁt Can Be Stolen When Closing

## Summary
Severity: Critical
Contest weight: 0.1534
Dataset id: 22052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a trader closes a position before settlement, there is currently no protection against slippage. As long as the trader possesses suﬃcient vEth/vGas to settle their debts, the closure of the position will be successful. This vulnerability could be exploited by an attacker to siphon off the trader's proﬁts by manipulating the price of the pool, causing the trader to swap at a premium that would be covered by their proﬁts. By ensuring enough is returned to cover the trader's debt, the attacker can retain the proﬁt minus fees.

## Recommendation
Implement a parameter for closing a position that includes slippage protection to prevent potential exploitation by malicious parties.
