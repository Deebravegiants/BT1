# [?] fix: RUSTSEC-2025-0134 (#9636)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-06
Source: https://github.com/iotaledger/iota/commit/f00d90937e7a42fb3dfd6e5c03561c9d8aab6b29
Type: security-commit

## Details
fix: RUSTSEC-2025-0134 (#9636)

# Description of change

This PR updates all dependencies that use the deprecated
`rustls-pemfile`.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes
