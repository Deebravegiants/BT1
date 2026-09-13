# [M] ALPINE-CVE-2021-0308

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-0308
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-0308
Type: osv

## Affected
- Alpine:v3.12: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.13: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.14: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.15: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.16: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.17: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.18: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.19: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.20: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.21: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.22: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.23: `gptfdisk` — affected >=0 <1.0.6-r0
- Alpine:v3.24: `gptfdisk` — affected >=0 <1.0.6-r0

## Details
In ReadLogicalParts of basicmbr.cc, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android; Versions: Android-8.1, Android-9, Android-10, Android-11, Android-8.0; Android ID: A-158063095.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-0308
