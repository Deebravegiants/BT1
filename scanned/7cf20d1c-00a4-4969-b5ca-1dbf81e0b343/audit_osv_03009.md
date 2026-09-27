# [M] ALPINE-CVE-2024-2466

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-2466
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2466
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.18: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.19: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.20: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.21: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.22: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.23: `curl` — affected >=8.5.0 <8.7.1-r0
- Alpine:v3.24: `curl` — affected >=8.5.0 <8.7.1-r0

## Details
libcurl did not check the server certificate of TLS connections done to a host specified as an IP address, when built to use mbedTLS.  libcurl would wrongly avoid using the set hostname function when the specified hostname was given as an IP address, therefore completely skipping the certificate check. This affects all uses of TLS protocols (HTTPS, FTPS, IMAPS, POPS3, SMTPS, etc).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2466
