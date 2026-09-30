# [C] Checks-effects-interations pattern is not always followed, which can be used to drain all tokens

## Summary
Severity: Critical
Contest weight: 0.1333
Dataset id: 15184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Here is a writeup about the pattern. Essentially state changes should be handled before interacting with external contracts (for example, when sending ETH via .call(""), to avoid reentrancy. Here is an example of the code not following it. _postWithdraw() should happen before sending ETH. So a user can call withdrawETH(), get execution when the ETH is sent, use the same note commitment (still not marked used) to swap on uniswap and double spend. This can be done in a loop to drain all tokens.

## Recommendation
Ensure that the codebase follows this pattern.
