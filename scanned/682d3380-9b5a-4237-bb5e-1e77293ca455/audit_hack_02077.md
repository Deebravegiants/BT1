# [C] 6.1 onTokenTransfer Wrong Accounting

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Critical Version 1 Code Corrected

When triggering onTokenTransfer with only one deposit, stake_amount is assumed to be 32 STAKE
but is not checked. This allows a depositor to call STAKE.transfer with 1 STAKE but to be accounted
for 32 in the Merkle tree.

Code corrected

In case of a single transfer the amount is set to the transferred amount specified. In batch transfers it is
set to 32 Ether. This behavior is coherent with the behavior of single deposits and batch deposits.
