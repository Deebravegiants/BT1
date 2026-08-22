# [?] fix[lang]: fix panic on function named `address` (#5196)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-07-22
Source: https://github.com/vyperlang/vyper/commit/730a2d36f1fca90be059c75681de5c942560ce0b
Type: security-commit

## Details
fix[lang]: fix panic on function named `address` (#5196)

this commit fixes a panic on methods named 'address'. the panic occured
during the construction of the user-facing error message, and was due to
'_id' on 'InterfaceT' being set too late.
