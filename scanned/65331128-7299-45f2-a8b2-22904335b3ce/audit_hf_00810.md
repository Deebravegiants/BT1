# [H] H-03 | Protocol Fees Are Donations

## Summary
Severity: High
Contest weight: 0.1032
Dataset id: 2546
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The interestFee and originationFee are fees that go to the protocol.
• Anyone can create a new BasePool and set the interestFee and originationFee while doing so.
Therefore the protocol fees are not enforced and act like donations instead. As it makes no economic sense for the BasePool owner to set these fees above 0 the protocol will probably lose a lot of money.

## Recommendation
Enforce the protocol fees.
