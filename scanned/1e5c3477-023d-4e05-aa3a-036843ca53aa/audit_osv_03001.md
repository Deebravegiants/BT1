# [M] ALPINE-CVE-2024-23337

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-23337
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23337
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.0-r0

## Details
jq is a command-line JSON processor. In versions up to and including 1.7.1, an integer overflow arises when assigning value using an index of 2147483647, the signed integer limit. This causes a denial of service. Commit de21386681c0df0104a99d9d09db23a9b2a78b1e contains a patch for the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23337
