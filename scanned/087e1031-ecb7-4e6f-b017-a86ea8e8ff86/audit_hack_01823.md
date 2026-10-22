# [H] ERC777 incompatibilities

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

As noted in [the README](eip-777).

Functions and events have been renamed, and the hooks `ERC777TokensRecipient` and `ERC777TokensSender` have been modified to add a `partition` parameter.

This means no tools that deal with standard ERC 777 contracts will work with this code's tokens.

#### Remediation

We suggest renaming these contracts to not use the term "ERC777", as they lack compatibility. Most importantly, we recommend _not_ using the interface names "ERC777TokensRecipient" and "ERC777TokensSender" when looking up the appropriate hook contracts via [ERC 1820](http://eips.ethereum.org/EIPS/eip-1820). Contracts that handle that interface will not be capable of handling the modified interface used here.
