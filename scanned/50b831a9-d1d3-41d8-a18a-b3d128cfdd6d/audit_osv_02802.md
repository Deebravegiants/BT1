# [M] ALPINE-CVE-2023-27535

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-27535
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27535
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.15: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.16: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.88.1-r1
- Alpine:v3.18: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.0.0-r0

## Details
An authentication bypass vulnerability exists in libcurl <8.0.0 in the FTP connection reuse feature that can result in wrong credentials being used during subsequent transfers. Previously created connections are kept in a connection pool for reuse if they match the current setup. However, certain FTP settings such as CURLOPT_FTP_ACCOUNT, CURLOPT_FTP_ALTERNATIVE_TO_USER, CURLOPT_FTP_SSL_CCC, and CURLOPT_USE_SSL were not included in the configuration match checks, causing them to match too easily. This could lead to libcurl using the wrong credentials when performing a transfer, potentially allowing unauthorized access to sensitive information.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27535
