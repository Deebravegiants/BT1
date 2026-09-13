# [H] ALPINE-CVE-2024-10224

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-10224
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-10224
Type: osv

## Affected
- Alpine:v3.21: `perl-module-scandeps` — affected >=0 <1.37-r0
- Alpine:v3.22: `perl-module-scandeps` — affected >=0 <1.37-r0
- Alpine:v3.23: `perl-module-scandeps` — affected >=0 <1.37-r0
- Alpine:v3.24: `perl-module-scandeps` — affected >=0 <1.37-r0

## Details
Qualys discovered that if unsanitized input was used with the library Modules::ScanDeps, before version 1.36 a local attacker could possibly execute arbitrary shell commands by open()ing a "pesky pipe" (such as passing "commands|" as a filename) or by passing arbitrary strings to eval().

## References
- https://security.alpinelinux.org/vuln/CVE-2024-10224
