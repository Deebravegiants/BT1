# [M] ALPINE-CVE-2024-10524

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-10524
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-10524
Type: osv

## Affected
- Alpine:v3.21: `wget` — affected >=0 <1.25.0-r0
- Alpine:v3.22: `wget` — affected >=0 <1.25.0-r0
- Alpine:v3.23: `wget` — affected >=0 <1.25.0-r0
- Alpine:v3.24: `wget` — affected >=0 <1.25.0-r0

## Details
Applications that use Wget to access a remote resource using shorthand URLs and pass arbitrary user credentials in the URL are vulnerable. In these cases attackers can enter crafted credentials which will cause Wget to access an arbitrary host.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-10524
