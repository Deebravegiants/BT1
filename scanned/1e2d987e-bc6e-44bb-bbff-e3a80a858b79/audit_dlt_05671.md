# [?] deps: update the `elliptic` to fix a vulnerability  (#8374)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2025-09-11
Source: https://github.com/ChainSafe/lodestar/commit/8644a83c623c7eda1830d90ec5d67f3aed5aeec3
Type: security-commit

## Details
deps: update the `elliptic` to fix a vulnerability  (#8374)

**Motivation**

Keep the dependencies safe from all vulnerabilities. 

**Description**

- Fix a `critical` level vulnerability. 

https://github.com/advisories/GHSA-fc9h-whq2-v747

It's not critical for our beacon node or validator implementation but
used in `@lodestar/prover` package.

**Steps to test or reproduce**

Run all tests
