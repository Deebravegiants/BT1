# [M] Use of `.send`

## Summary
Severity: Medium
Contest weight: 0.1412
Dataset id: 8139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[ForgottenRunesWarriorsMinter.sol#L610](https://github.com/code-423n4/2022-05-runes/blob/main/contracts/ForgottenRunesWarriorsMinter.sol#L610)  
[ForgottenRunesWarriorsMinter.sol#L618](https://github.com/code-423n4/2022-05-runes/blob/main/contracts/ForgottenRunesWarriorsMinter.sol#L618)  
[ForgottenRunesWarriorsGuild.sol#L164](https://github.com/code-423n4/2022-05-runes/blob/main/contracts/ForgottenRunesWarriorsGuild.sol#L164)  

The `.send()` function intends to transfer an ETH amount with a fixed amount of 2300 gas. This function is not equipped to handle changes in the underlying `.send()` and `.transfer()` functions which may supply different amounts of gas in the future. Additionally, if the recipient implements a fallback function containing some sort of logic, this may inevitably revert, meaning the vault and owner of the contract will never be able to call certain sensitive functions.

## Recommendation
Consider using `.call()` instead with the checks-effects-interactions pattern implemented correctly. Careful consideration needs to be made to prevent reentrancy.

Determined the stake is high here and therefore Medium Risk.
