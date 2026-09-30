# [M] Reentrancy in `depositBribeERC20` function

## Summary
Severity: Medium
Contest weight: 0.4454
Dataset id: 1671
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[BribeVault.sol#L164-L205](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L164-L205)

```solidity
depositBribeERC20``` function in ``BriveVault``` is reentrant in line 187, where an address supplied by the caller is called.

A bad actor that has `DEPOSITOR_ROLE` and is a contract can execute a folowing attack:

1. Create a dummy token contract, reentrant in the transferFrom() function. All tokens are approved to the `BriveVault` and the attacker contract has unlimited tokens. Reentrancy aims back to a function in the attacker contract, which calls `depositBribeERC20` again.
2. The first call by the contract must use a novel `bribeIdentifier`. `token` is set to a dummy contract and `amount` to `uint(-2)`.
3. All checks pass, `transferFrom` is called, which calls attacker contract, which can call `depositBribeERC20` again, this time will transfer 1 wei of a valuable token, using the same `bribeIdentifier`. All checks pass as the previous token hasn’t been registered yet. Then, a valid transfer happens. After that, the amount is set to 1 wei and the token is saved. Event is emitted and the function returns value. Then, attacker function returns and dummy token returns. The operation is to increment amount in storage by the transfer value, which increases `b.amount` to the maximum integer. The token is nonzero, so the if statement is passed.

Thus, an attacker can grant any amount of tokens from `BriveVault` to a certain bribe, stealing all the funds once the bribe will be withdrawn.

## Recommendation
Set bribe token before the transfer is made.

I do believe re-entrancy is possible, so I recommend the sponsor to add the `nonReentrant` modifier to the deposit function.
 
I’ll keep the finding separate [from M-02] as this deals with reEntrancy.  
Mitigation would be to enforce a bribeIdentifier to be used for a specific token (and it being enforced), as well as adding `nonReentrant`.
 
Because the function is permissioned, I believe medium severity to be more appropriate.
