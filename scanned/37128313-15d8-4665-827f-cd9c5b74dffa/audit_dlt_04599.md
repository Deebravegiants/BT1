# [H] Function rescueERC20 can be exploited to acquire the owner power

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/87
Type: sherlock-finding

## Details
zimu

high

# Function rescueERC20 can be exploited to acquire the owner power

## Summary
Since `FeeBuyback.rescueERC20` is called by the owner, a malicious user can utilize unsafe transfer in `FeeBuyback.rescueERC20` to acuqire the owner power, and to sweep funds from contract.

## Vulnerability Detail
A malicious user can possibly use the following steps to take the owner permission:
1.  The user implements an ERC20 contract with a callback in its `transfer` function, and names this contract as `WETH` for disguise;
2.  To depoly this malicious contract, the user generates addresses by colllisions to make the head and the tail part of the deployed address same or almost the same as the real address of `WETH` contract;
3.  Then, the user sends its fake `WETH` to the address of contract `FeeBuyback`, and pretends it to be an accident that originally intends to send to a similar address or casual clicks to send to a memorized address;
4.  The user asks telcoin team for help, and finally the owner may find these `WETH` to send them back to the user, and could fall into the trap of callback to surrender the owner control to the user.

## Impact
Function rescueERC20 can be exploited to surrender the owner control.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97

## Tool used
Manual Review

## Recommendation
Add a nonReentrant modifier to `FeeBuyback.rescueERC20`, and better, use `SafeERC20` library for safe transfer.
