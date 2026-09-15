# [M] 6.2 Missing Check for Whitelisting

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 2 Code Corrected

bankTransfer allows the admin to send money from the bank to a recipient. The recipient must be
whitelisted by having the MULTISIG_ROLE. However, the sender is sanitized while the receiver is not.


The error message emitted on revert i.e., Recipient must be whitelisted, also implies that the
receiver should be sanitized.

Code corrected:

The function bankTransfer has been removed.
