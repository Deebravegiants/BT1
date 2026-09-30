# [M] withdrawAVAX

## Summary
Severity: Medium
Contest weight: 0.0745
Dataset id: 1499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LaunchEvent.sol the withdrawAVAX() function makes an external call to the msg.sender by way of _safeTransferAVAX. This allows the caller to reenter this and other functions in this and other protocol files. To prevent reentrancy and cross function reentrancy there should be reentrancy guard modifiers placed on the withdrawAVAX() function and any other function that makes external calls to the caller.

## Recommendation
Add reentrancy guard modifier to withdrawAVAX() function.

Resolved using CEI: <https://github.com/traderjoe-xyz/rocket-joe/commit/dbd19cc400abb5863edfc0443dd408ba5ae3e99a>
