# [M] neqo-qpack has iInteger overflow in qpack dynamic table indexing

## Summary
Severity: Medium
Advisory: GHSA-6w86-wgwq-rgq8
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-6w86-wgwq-rgq8
Type: github-advisory

## Affected
- crates.io: `neqo-qpack` — affected >=0

## Details
### Summary

An unsanitized qpack index can lead to an integer overflow, panicing in debug mode, accessing the wrong or no dynamic table entry in release mode.

What does this mean for Firefox? Firefox runs Neqo in release mode. A malicious remote can cause its own QUIC connection to fail to use qpack, i.e. compression, or enter an inconsistent state. The remote can not crash Firefox, nor affect other QUIC connections. 

### Details

See fuzz report in https://github.com/mozilla/neqo/issues/3406.

### PoC
See test in pull request.

### Impact
All Firefox users. Though vulnerability likely scoped to same connection, i.e. low impact.

## References
- https://github.com/mozilla/neqo/security/advisories/GHSA-6w86-wgwq-rgq8
- https://github.com/mozilla/neqo/issues/3406
- https://github.com/mozilla/neqo
