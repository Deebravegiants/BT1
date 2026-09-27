# [H] 6.3 Retain Ownership of Credit Account

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

In Gearbox, Credit Accounts are reused after they have been returned to the factory. Due to a reentrancy
issue, account ownership can be retained and after the next user got this credit account assigned, the
previous owner may access its funds belonging to the new owner.

Function transferAccountOwnership does not feature the non nonReentrant modifier and hence
can be executed during another operation. Consider the follwowing scenario:

Alice owns a healthy credit account 0xA which holds some WETH balance.

```
1.Alice prepares a contract that allows her to execute all necessary actions. As a first step, the credit
account ownership is transferred to this contract.
```

```
2.The credit account is repaid using repayCreditAccount specifying the contract as to address.
This transfers all assets to the provided to address. Notably the WETH asset is unwraped into
Ether, the Ether is transferred in a call to the reciepient's address to. This call executes code at the
contract.
3.At the specified to address a contract exists. This contract transfers the ownership of the credit
account onwards to another address (newAddress) Alice controls. This means that
creditAccounts[newAddress] will point to the credit account
4.The closure of the credit account continues as normal. All assets are transferred to address to, the
debt is repaid to the pool and the credit account is returned to the AccountFactory.
5.Next delete creditAccounts[borrower]; is executed, this should delete the assignment of
this credit account to the borrower. However, as we already transferred the ownership from
borrower which is the contract address back to Alice, creditAccounts[borrower] contains
no entry at this point and deleting it has no effect.
```
At the end of this sequence, the credit account has been returned to the AccountFactory but the entry
creditAccounts[newAddress] in this CreditManager still points to this account.

The next time this CreditAccount is reused at the same CreditManager by a new user, due to the
entry in creditAccounts Alice will still have access to this account and can collect its funds by e.g.
closing or repaying the account.

Code corrected:

transferAccountOwnership() now features the nonReentrant modifier. Hence, the reentrancy
issue described is no longer possible.
