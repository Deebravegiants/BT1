# [M] M-09 | A Portion Of Frozen Fees Will Remain Frozen

## Summary
Severity: Medium
Contest weight: 0.0959
Dataset id: 2197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the withdraw2contract flow the amount of funds and the fee will be frozen. Then at the end of the flow these amounts are intended to be unfrozen. However, there will be small difference between the amount frozen and unfrozen. This will happen when convertDecimal is called and the destination chain decimals are less than the sending chain. In this case there will be some precision loss and while X amount of funds are frozen at the beginning only X - Y will be unfrozen. Where Y equals the precision loss.

## Recommendation
Adjust fee amount and withdraw amount so that there is no precision loss prior to freezing the funds. This can be done by truncating the amount to the destination decimals and then expanding it back to the senders decimals. This will ensure that the amount frozen and unfrozen are the same.
