# [?] fix: data race in signer fields in consortium v2 (#207)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2023-02-23
Source: https://github.com/axieinfinity/ronin-archive/commit/d0113ae528ee90efb1b3171a55e00b2599f1634b
Type: security-commit

## Details
fix: data race in signer fields in consortium v2 (#207)

This commit makes all read of signer fields in consortium v2 hold read mutex
lock to synchronize with read mutex lock in Consortium.Authorize function.
