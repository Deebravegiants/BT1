# [H] ERC5095.sol - approval based `redeem` and `withdraw` will not be safe.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/192
Type: sherlock-finding

## Details
ak1

high

# ERC5095.sol - approval based `redeem` and `withdraw` will not be safe.

## Summary

Approval based redeem and withdraw functionalities will not be safe. The malicious approved address can transfer the fund either to his/her own account or  any other account that they wish,

## Vulnerability Detail

When look at the approval based withdraw and redeem, 

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L246

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L272

the fund is sent to address `r` that mean the address `r` can be any address. either it can be `msg.sender` or any other address that is set by msg.sender.

The problem here is, the msg.sender can transfer the fund wither his/her own account or to the account that they want.

## Impact

The malicious approved address can take out funds either to his/her account and to any other account that they wish.

imo, this will not be safe. actual owner will loose his/her control on their fund.

## Code Snippet

withdraw - approval based.

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L228-L249

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L262-L275

Redeem - approval based 


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/192_
