# [M] 6.2 New Owner Cannot Permit

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

In AccountGuard, when an owner is initially set by the factory they also receive an entry in the
allowed[caller][target] mapping. However, when changeOwner() is called, the new owner only
receives an entry in the owners mapping but is not added to the allowed mapping. Hence, the new
owner cannot call permit on the proxy they now own.

Note that not even someone else who is allowed to permit on the proxy can admit the owner, as
permitting the owner will revert with "account-guard/cant-deny-owner". The only way to allow the
new owner would be to transfer ownership to someone else who is already allowed to permit.

The owner would still be able to make transactions from the proxy, as canCall() always returns true for
the owner, even if they are not allowed.

Code corrected

changeOwner now adds the new owner to the allowed addresses.
