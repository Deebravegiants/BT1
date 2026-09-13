# [?] fix memory corruption with calls inside events

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-08-04
Source: https://github.com/vyperlang/vyper/commit/cea5dd89dab17031b7c508bc5b9feaa47ff2e7db
Type: security-commit

## Details
fix memory corruption with calls inside events

The key is to make sure the memory is allocated and registered with the
context variable BEFORE evaluating the expressions inside the event (in
case any of them make internal calls)

fixes #1476
