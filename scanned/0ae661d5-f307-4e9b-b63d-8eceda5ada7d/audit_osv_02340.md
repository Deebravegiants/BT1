# [M] ALPINE-CVE-2021-44532

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-44532
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44532
Type: osv

## Affected
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.10-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.19.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.19.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.17: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.18: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.19: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.20: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.21: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.24: `nodejs` — affected >=0 <16.13.2-r0

## Details
Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 converts SANs (Subject Alternative Names) to a string format. It uses this string to check peer certificates against hostnames when validating connections. The string format was subject to an injection vulnerability when name constraints were used within a certificate chain, allowing the bypass of these name constraints.Versions of Node.js with the fix for this escape SANs containing the problematic characters in order to prevent the injection. This behavior can be reverted through the --security-revert command-line option.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44532
