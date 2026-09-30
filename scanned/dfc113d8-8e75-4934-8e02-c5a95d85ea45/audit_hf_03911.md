# [M] Bypassing the isOpen modifier in the pools

## Summary
Severity: Medium
Contest weight: 0.1007
Dataset id: 20210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Bypassing the isOpen modifier in the pools Currently, GLIF has a modifier isOpen that "pauses" the interaction with several functions from the pool, some of them are: borrow , pay , deposit and mint . This modifier can be set to false for several reasons, upgrading and agent, or simply because there is a security issue and you need to pause the system. This modifier can be actually bypassed by triggering either receive or fallback in the pool contract, because they call the internal function to deposit instead of the external one that has the modifier. System can still be interacted with when it must be paused. This could cause issues when the contract is paused.

## Recommendation
add the modifier also in the internal function
