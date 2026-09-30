# [H] ALPINE-CVE-2021-44531

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-44531
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44531
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
Accepting arbitrary Subject Alternative Name (SAN) types, unless a PKI is specifically defined to use a particular SAN type, can result in bypassing name-constrained intermediates. Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 was accepting URI SAN types, which PKIs are often not defined to use. Additionally, when a protocol allows URI SANs, Node.js did not match the URI correctly.Versions of Node.js with the fix for this disable the URI SAN type when checking a certificate against a hostname. This behavior can be reverted through the --security-revert command-line option.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44531
