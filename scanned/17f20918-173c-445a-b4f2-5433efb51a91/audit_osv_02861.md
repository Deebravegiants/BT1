# [C] ALPINE-CVE-2023-38703

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-38703
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38703
Type: osv

## Affected
- Alpine:v3.18: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.14-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.14-r0

## Details
PJSIP is a free and open source multimedia communication library written in C with high level API in C, C++, Java, C#, and Python languages. SRTP is a higher level media transport which is stacked upon a lower level media transport such as UDP and ICE. Currently a higher level transport is not synchronized with its lower level transport that may introduce use-after-free issue. This vulnerability affects applications that have SRTP capability (`PJMEDIA_HAS_SRTP` is set) and use underlying media transport other than UDP. This vulnerability’s impact may range from unexpected application termination to control flow hijack/memory corruption. The patch is available as a commit in the master branch.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38703
