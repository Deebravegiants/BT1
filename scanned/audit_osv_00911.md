# [C] ALPINE-CVE-2018-10933

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-10933
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10933
Type: osv

## Affected
- Alpine:v3.10: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.11: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.5: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.6: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.7: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.8: `libssh` — affected >=0.6.0 <0.7.6-r0
- Alpine:v3.9: `libssh` — affected >=0.6.0 <0.7.6-r0

## Details
A vulnerability was found in libssh's server-side state machine before versions 0.7.6 and 0.8.4. A malicious client could create channels without first performing authentication, resulting in unauthorized access.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10933
