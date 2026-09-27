# [H] ALPINE-CVE-2020-15778

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15778
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15778
Type: osv

## Affected
- Alpine:v3.19: `openssh` — affected >=0 <8.3_p1-r0
- Alpine:v3.20: `openssh` — affected >=0 <8.3_p1-r0
- Alpine:v3.21: `openssh` — affected >=0 <8.3_p1-r0
- Alpine:v3.22: `openssh` — affected >=0 <8.3_p1-r0
- Alpine:v3.23: `openssh` — affected >=0 <8.3_p1-r0
- Alpine:v3.24: `openssh` — affected >=0 <8.3_p1-r0

## Details
scp in OpenSSH through 8.3p1 allows command injection in the scp.c toremote function, as demonstrated by backtick characters in the destination argument. NOTE: the vendor reportedly has stated that they intentionally omit validation of "anomalous argument transfers" because that could "stand a great chance of breaking existing workflows."

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15778
