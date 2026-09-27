# [M] A malicious guardian can steal funds

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

A guardian is signing every message that should be submitted as a payment channel update. 
A guardian's two main things to verify are: `blockNumber` and the fact that the `sender` has enough funds.

There are two main attack vectors for the malicious guardian:

* It's possible to conspire with the previous owner of the account and submit the old `blockNumber`. This allows them to drain the account.

* A guardian can also conspire with the `sender` and send more funds to multiple channels than funds in the account.

#### Recommendation

Reduce the system's reliance on single points of failure like the guardians.
