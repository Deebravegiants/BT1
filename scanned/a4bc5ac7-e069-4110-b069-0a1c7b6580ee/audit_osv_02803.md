# [M] ALPINE-CVE-2023-27536

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-27536
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27536
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
An authentication bypass vulnerability exists libcurl <8.0.0 in the connection reuse feature which can reuse previously established connections with incorrect user permissions due to a failure to check for changes in the CURLOPT_GSSAPI_DELEGATION option. This vulnerability affects krb5/kerberos/negotiate/GSSAPI transfers and could potentially result in unauthorized access to sensitive information. The safest option is to not reuse connections if the CURLOPT_GSSAPI_DELEGATION option has been changed.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27536
