# [M] no 0 address check

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-22
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/5
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x40a0b5fa589a4e38b5035763ef5900c20c41da40b0744fe0fc75277dd3335c50
**Severity:** medium

**Description:**
**Description**\
loss of funds for the user due to lack of 0 address check
**Attack Scenario**\
There isnt' 0 address check in alot of places in the code which can cause problem even loss of funds like in the function `withdraw()` of 	`ionPool.sol` so a little typo can cause alot of loss for the user
**Recommendation**
add 0 address check to mitigate this problem
