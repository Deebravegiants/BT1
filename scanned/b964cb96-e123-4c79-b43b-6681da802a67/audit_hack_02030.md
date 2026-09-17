# [M] 6.11 takeOut May Break the Account List

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The configurator can take out an account by calling AccountFactory.takeOut(). During account
removal, there is no check whether this is the tail nor is the tail updated in case this account is taken out.
Should the tail account be taken out this is problematic:

New accounts added will not be connected to the original list, hence they cannot be taken using
takeCreditAccount() which takes the head of the original list.

Similarly, returned accounts will be added to the list after the removed tail account which no longer
exists in the list. Again, the connection to the original list starting at head is interrupted and these
accounts cannot be used anymore.

Code Corrected:

The implementation has been extended to correctly update tail when the last account is taken out.
