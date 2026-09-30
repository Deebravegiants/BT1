# [M] Blacklisted accounts can still withdraw from

## Summary
Severity: Medium
Contest weight: 0.0838
Dataset id: 20345
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
L2CustomERC20Permit blocks burns from blacklisted accounts. The issue is that when withdrawing, the from address is always the exchange contract which makes the blacklist ineffective.
#L476-L482
When withdrawing from the exchange, the exchange contract always calls the withdrawTo method. This means that the from address passed to the ERC20 will ALWAYS be the exchange's address rather than the user's address. The result is that blacklisting the from is ineffective.
Blacklist is ineffective for preventing withdraws from blacklisted addresses

## Recommendation
Blacklisting burn needs to be redesigned
