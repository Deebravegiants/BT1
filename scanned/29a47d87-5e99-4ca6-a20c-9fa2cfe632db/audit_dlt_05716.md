# [?] Fix zcash-cli crash when printing help message

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2023-04-15
Source: https://github.com/zcash/zcash/commit/14c11c385a5dc2ebce407b8dcbc96c8c3ddd88ca
Type: security-commit

## Details
Fix zcash-cli crash when printing help message

When a `zcash-cli` command fails, it attempts to print the help message for the command. However,
making the `help` call can also fail, and there was a bug in this check, so that we tried to display
the help message when the `help` call failed, and tried to display the error when the `help` call
succeeded – both leading to an assertion failure.

This also makes some minor changes to the output formatting.

Fixes #6561
