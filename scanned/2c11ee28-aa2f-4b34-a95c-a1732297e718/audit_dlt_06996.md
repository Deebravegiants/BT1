# [M] Reentrancy in `depositBribeERC20` function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-redacted-cartel
Published: 2022-02-17
Source: https://github.com/code-423n4/2022-02-redacted-cartel-findings/issues/122
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L164-L205


# Vulnerability details

## Impact

`depositBribeERC20` function in `BriveVault` is reentrant in line 187, where an address supplied by the caller is called.

A bad actor that has `DEPOSITOR_ROLE` and is a contract can execute a folowing attack:

1. Create a dummy token contract, reentrant in the transferFrom() function. All tokens are approved to the `BriveVault` and the attacker contract has unlimited tokens. Reentrancy aims back to a function in the attacker contract, which calls `depositBribeERC20` again.
2. The first call by the contract must use a novel `bribeIdentifier`. `token` is set to a dummy contract and `amount` to `uint(-2)`.
3. All checks pass, `transferFrom` is called, which calls attacker contract, which can call `depositBribeERC20` again, this time will transfer 1 wei of a valuable token, using the same `bribeIdentifier`. All checks pass as the previous token hasn't been registered yet. Then, a valid transfer happens. After that, the amount is set to 1 wei and the token is saved. Event is emitted and the function returns value. Then, attacker function returns and dummy token returns. The operation is to increment amount in storage by the transfer value, which increases `b.amount` to the maximum integer. The token is nonzero, so the if statement is passed.

Thus, an attacker can grant any amount of tokens from `BriveVault` to a certain bribe, stealing all the funds once the bribe will be withdrawn.

## Recommended Mitigation Steps

Set bribe token before the transfer is made.
