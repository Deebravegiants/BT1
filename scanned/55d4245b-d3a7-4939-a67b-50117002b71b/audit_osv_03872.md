# [M] ALPINE-CVE-2026-5947

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-5947
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5947
Type: osv

## Affected
- Alpine:v3.20: `bind` — affected >=9.20.0 <9.18.49-r0
- Alpine:v3.21: `bind` — affected >=9.20.0 <9.18.49-r0
- Alpine:v3.22: `bind` — affected >=9.20.0 <9.20.23-r0
- Alpine:v3.23: `bind` — affected >=9.20.0 <9.20.23-r0
- Alpine:v3.24: `bind` — affected >=9.20.0 <9.20.23-r0

## Details
Undefined behavior may result due to a race condition leading to a use-after-free violation.  If BIND receives an incoming DNS message signed with SIG(0), it begins work to validate that signature.  If, during that validation, the "recursive-clients" limit is reached (as would occur during a query flood), and that same DNS message is discarded per the limit, there is a brief window of time while the SIG(0) validation may attempt to read the now-discarded DNS message.
This issue affects BIND 9 versions 9.20.0 through 9.20.22, 9.21.0 through 9.21.21, and 9.20.9-S1 through 9.20.22-S1.
BIND 9 versions 9.18.28 through 9.18.49 and 9.18.28-S1 through 9.18.49-S1 are NOT affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5947
