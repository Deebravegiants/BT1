# [C] ALPINE-CVE-2017-7614

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-7614
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7614
Type: osv

## Affected
- Alpine:v3.10: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.11: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.12: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.13: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.14: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.15: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.16: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.17: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.18: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.19: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.20: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.21: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.22: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.23: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.24: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.4: `binutils` — affected >=0 <2.26-r1
- Alpine:v3.5: `binutils` — affected >=0 <2.27-r1
- Alpine:v3.6: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.7: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.8: `binutils` — affected >=0 <2.28-r1
- Alpine:v3.9: `binutils` — affected >=0 <2.28-r1

## Details
elflink.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has a "member access within null pointer" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via an "int main() {return 0;}" program.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7614
