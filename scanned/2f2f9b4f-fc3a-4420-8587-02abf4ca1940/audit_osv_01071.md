# [H] ALPINE-CVE-2018-18820

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-18820
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18820
Type: osv

## Affected
- Alpine:v3.10: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.11: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.12: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.13: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.14: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.15: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.16: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.17: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.18: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.19: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.2: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.20: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.21: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.22: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.23: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.3: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.4: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.5: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.6: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.7: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.8: `icecast` — affected >=0 <2.4.4-r0
- Alpine:v3.9: `icecast` — affected >=0 <2.4.4-r0

## Details
A buffer overflow was discovered in the URL-authentication backend of the Icecast before 2.4.4. If the backend is enabled, then any malicious HTTP client can send a request for that specific resource including a crafted header, leading to denial of service and potentially remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18820
