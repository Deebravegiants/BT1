# [M] 6.4 Renegotiation Replays Possible

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

Renegotiation is a feature that allows the lender to give the borrower an alternative offer after the loan
has been created. However, replay attacks may be possible here.

As more loan types will appear, more loan coordinator contracts could be deployed. Following could
occur:

```
1.Borrower A has a loan connected to Coordinator A. Borrower B has a loan connected to Coordinator
B. The lender is in both cases the same.
2.Borrower A and the lender renegotiate the lending terms.
```
```
3.Borrower B replays the signature while the signature is not expired yet.
4.The lender has renegotiated two positions instead of only one.
```
This attack works as long as the data provided to renegotiation functions is the same.

Code corrected:

Now, the contract address is signed. Thus, the signature can only be used on the valid contract.
