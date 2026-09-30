# [M] totalMembers Can Be Manipulated

## Summary
Severity: Medium
Contest weight: 0.0726
Dataset id: 14283
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lockTokens() function is used by a user to lock tokens and gain voting power. This function however, can be
used to manipulate the totalMembers variable because it accepts zero amount as an input. A malicious user can call
lockTokens() as many times as they want to increase the totalMembers variable.
Similarly, function withdrawTokens() can be used to decrease the totalMembers by withdrawing zero amount (see
DXD-01)

## Recommendation
The testing team recommends preventing zero amount as an input on lockTokens() and withdrawTokens().
