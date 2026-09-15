# [M] Adversary can vote during periods of high gas fees to burn a large amount of treasury funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/32
Type: sherlock-finding

## Details
0x52

medium

# Adversary can vote during periods of high gas fees to burn a large amount of treasury funds

## Summary

Voters are refunded when they cast their votes. If they vote while gas prices are extremely high they will burn a large amount of treasury funds

## Vulnerability Detail

Voters are refunded when they cast their votes. There is no cap on the base gas fee that the contract will refund to the voter. If they vote while gas prices are extremely high they will burn a large amount of treasury funds.

## Impact

Adversary can purposely vote during periods of high gas to use up large amounts of treasury funds

## Code Snippet

https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/utils/Refundable.sol#L23-L42

## Tool used

Manual Review

## Recommendation

Refundable#RefundGas should implement a max base fee it is willing to refund such as 50 gwei
