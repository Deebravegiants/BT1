# [M] M-04 | No Enforcement Of Required Bridging Fee In sendMessage

## Summary
Severity: Medium
Contest weight: 0.0636
Dataset id: 2192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The sendMessage function in VaultCrossChainManager calculates a MessagingFee via _quote but never checks whether the user-supplied msg.value actually matches the required bridging fee. Because there is no comparison between messageFee.nativeFee and msg.value, the function can be underfunded without reverting.

## Recommendation
Enforce that msg.value is at least equal to the calculated bridging fee. For example, add a check like require(msg.value == messageFee.nativeFee, "Insufficient bridging fee"); to ensure that the user has paid for the fee.
