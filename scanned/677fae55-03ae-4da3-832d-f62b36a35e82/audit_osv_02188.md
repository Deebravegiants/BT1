# [C] ALPINE-CVE-2021-29922

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-29922
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29922
Type: osv

## Affected
- Alpine:v3.19: `rust` — affected >=0 <1.52.1-r1
- Alpine:v3.20: `rust` — affected >=0 <1.52.1-r1
- Alpine:v3.21: `rust` — affected >=0 <1.52.1-r1
- Alpine:v3.22: `rust` — affected >=0 <1.52.1-r1
- Alpine:v3.23: `rust` — affected >=0 <1.52.1-r1
- Alpine:v3.24: `rust` — affected >=0 <1.52.1-r1

## Details
library/std/src/net/parser.rs in Rust before 1.53.0 does not properly consider extraneous zero characters at the beginning of an IP address string, which (in some situations) allows attackers to bypass access control that is based on IP addresses, because of unexpected octal interpretation.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29922
