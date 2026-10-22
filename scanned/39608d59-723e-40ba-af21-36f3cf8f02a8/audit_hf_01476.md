# [H] H-3 BURNUNLOCKCODE does not validate p.tokenIn

## Summary
Severity: High
Contest weight: 0.1843
Dataset id: 7829
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• RouterV2.sol#L120
The BURNUNLOCKCODE function does not validate p.tokenIn, which can lead to the theft of funds. If the backend is compromised, an attacker could insert a malicious contract as the p.tokenIn parameter into the BURNUNLOCKCODE operation. This would result in the possibleAdapter being set to the fake p.tokenIn, enabling all subsequent calls to it to proceed without any monetary cost. This vulnerability could allow an attacker to unlock any token on subsequent chains, provided it is returned from the possibleAdapter.originalToken() function.

## Recommendation
We recommend implementing strict validation of the p.tokenIn parameter to conﬁrm its authenticity as a legitimate and trusted contract. Additionally, we recommend implementing security mechanisms such as whitelisting or signature veriﬁcation to authenticate the origin and integrity of the p.tokenIn parameter. This will help prevent unauthorized contracts from being exploited through BURNUNLOCKCODE and other sensitive operations.
