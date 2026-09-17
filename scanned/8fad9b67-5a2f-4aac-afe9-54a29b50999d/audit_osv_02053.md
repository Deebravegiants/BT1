# [M] ALPINE-CVE-2021-20208

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-20208
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20208
Type: osv

## Affected
- Alpine:v3.10: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.11: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.12: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.13: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.14: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.15: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.16: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.17: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.18: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.19: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.20: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.21: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.22: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.23: `cifs-utils` — affected >=4.0 <6.13-r0
- Alpine:v3.24: `cifs-utils` — affected >=4.0 <6.13-r0

## Details
A flaw was found in cifs-utils in versions before 6.13. A user when mounting a krb5 CIFS file system from within a container can use Kerberos credentials of the host. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20208
