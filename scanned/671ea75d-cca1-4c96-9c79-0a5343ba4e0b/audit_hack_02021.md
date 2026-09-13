# [H] 6.2 Non-Accessible Credit Accounts

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

The transferAccountOwnership function of a CreditManager contract allows the owner of a credit
account to transfer it onwards to a new owner. Per CreditManager an address is only allowed to hold one
credit account. trasferAccountOwnerhip(). However, there is no check on whether the recipient
already holds a credit account at this CreditManager contract and simply overwrites the entry for the
credit account of the recipient. Hence a credit account which holds funds can become non-accessible
and its funds will be trapped.

Code corrected:

In the updated code the transferAccountOwnership function no longer overwrites an existing credit
account entry of the recipient, hence the issue no longer exists.
