# [M] ALPINE-CVE-2021-28363

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28363
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28363
Type: osv

## Affected
- Alpine:v3.14: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.15: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.16: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.17: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.18: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.19: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.20: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.21: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.22: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.23: `py3-urllib3` — affected >=0 <1.26.4-r0
- Alpine:v3.24: `py3-urllib3` — affected >=0 <1.26.4-r0

## Details
The urllib3 library 1.26.x before 1.26.4 for Python omits SSL certificate validation in some cases involving HTTPS to HTTPS proxies. The initial connection to the HTTPS proxy (if an SSLContext isn't given via proxy_config) doesn't verify the hostname of the certificate. This means certificates for different servers that still validate properly with the default urllib3 SSLContext will be silently accepted.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28363
