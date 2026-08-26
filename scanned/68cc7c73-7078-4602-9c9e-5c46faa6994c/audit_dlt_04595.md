# [M] SimplePlugin and StakingModule ERC20 Tokens with fee on transfer are not supported

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/101
Type: sherlock-finding

## Details
Deivitto

medium

# SimplePlugin and StakingModule ERC20 Tokens with fee on transfer are not supported

## Summary
SimplePlugin and StakingModule ERC20 Tokens with fee on transfer are not supported
## Vulnerability Detail
There are ERC20 tokens that charge fee for every `transfer()` / `transferFrom()`.

## Impact
`claim` and `_exit` functions assumes that the received amount is the same as the transfer amount, and returns it, while the actual transferred amount can be lower for those tokens.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/SimplePlugin.sol#L95-L100
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L309-L313
## Tool used

Manual Review

## Recommendation
Consider comparing before and after balance to get the actual transferred amount.
