# [C] ALPINE-CVE-2016-7944

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7944
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7944
Type: osv

## Affected
- Alpine:v3.2: `libxfixes` — affected >=0 <5.0.1-r1
- Alpine:v3.3: `libxfixes` — affected >=0 <5.0.1-r2

## Details
Integer overflow in X.org libXfixes before 5.0.3 on 32-bit platforms might allow remote X servers to gain privileges via a length value of INT_MAX, which triggers the client to stop reading data and get out of sync.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7944
