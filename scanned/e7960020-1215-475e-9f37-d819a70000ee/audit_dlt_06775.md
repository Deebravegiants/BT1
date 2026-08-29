# [M] Add a timelock to `setPlatformFee()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-joyn
Published: 2022-04-01
Source: https://github.com/code-423n4/2022-03-joyn-findings/issues/112
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-joyn/blob/main/splits/contracts/SplitFactory.sol#L120
https://github.com/code-423n4/2022-03-joyn/blob/main/royalty-vault/contracts/RoyaltyVault.sol#L67


# Vulnerability details

## Impact
It is a good practice to give time for users to react and adjust to critical changes. A timelock provides more guarantees and reduces the level of trust required, thus decreasing risk for users. It also indicates that the project is legitimate.

Here, no timelock capabilities seem to be used

I believe this impacts multiple users enough to make them want to react / be notified ahead of time.

## Recommended Mitigation Steps
Consider adding a timelock to `setPlatformFee()`
