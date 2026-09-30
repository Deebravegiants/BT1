# [M] M-02 | Ordered Nonce Flag Should Only Be Set Once

## Summary
Severity: Medium
Contest weight: 0.0793
Dataset id: 21583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OrderOFT and OrderAdapter contracts are initialized with orderedNonce flag enabled, although owner can turn this flag on and off as pleased using setOrderedNonce. When orderedNonce is set to false, messages can be executed in any order, increasing the maxReceivedNonce. If the orderedNonce is turned on back again, there will be issues with messages that were not executed with lower nonces, as the only acceptable nonce will be maxReceivedNonce + 1.

## Recommendation
Remove the owner function to set the orderedNonce flag. Alternatively, only allow to turn it off and never be able to turn it back on again.
