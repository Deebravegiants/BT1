# [C] ALPINE-CVE-2019-3822

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-3822
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3822
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.7: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.8: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.9: `curl` — affected >=0 <7.64.0-r0

## Details
libcurl versions from 7.36.0 to before 7.64.0 are vulnerable to a stack-based buffer overflow. The function creating an outgoing NTLM type-3 header (`lib/vauth/ntlm.c:Curl_auth_create_ntlm_type3_message()`), generates the request HTTP header contents based on previously received data. The check that exists to prevent the local buffer from getting overflowed is implemented wrongly (using unsigned math) and as such it does not prevent the overflow from happening. This output data can grow larger than the local buffer if very large 'nt response' data is extracted from a previous NTLMv2 header provided by the malicious or broken HTTP server. Such a 'large value' needs to be around 1000 bytes or more. The actual payload data copied to the target buffer comes from the NTLMv2 type-2 response header.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3822
