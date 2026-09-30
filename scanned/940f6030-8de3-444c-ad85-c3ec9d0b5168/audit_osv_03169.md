# [M] ALPINE-CVE-2024-8096

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-8096
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-8096
Type: osv

## Affected
- Alpine:v3.18: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.19: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.20: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.21: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.22: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.23: `curl` — affected >=7.41.0 <8.10.0-r0
- Alpine:v3.24: `curl` — affected >=7.41.0 <8.10.0-r0

## Details
When curl is told to use the Certificate Status Request TLS extension, often referred to as OCSP stapling, to verify that the server certificate is valid, it might fail to detect some OCSP problems and instead wrongly consider the response as fine.  If the returned status reports another error than 'revoked' (like for example 'unauthorized') it is not treated as a bad certficate.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-8096
