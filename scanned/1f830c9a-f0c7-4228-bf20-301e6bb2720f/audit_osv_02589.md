# [H] ALPINE-CVE-2022-33742

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-33742
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33742
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r3
- Alpine:v3.14: `xen` — affected >=0 <4.15.3-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.3-r0
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r3
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r4
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r4

## Details
Linux disk/nic frontends data leaks T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Linux Block and Network PV device frontends don't zero memory regions before sharing them with the backend (CVE-2022-26365, CVE-2022-33740). Additionally the granularity of the grant table doesn't allow sharing less than a 4K page, leading to unrelated data residing in the same 4K page as data shared with a backend being accessible by such backend (CVE-2022-33741, CVE-2022-33742).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33742
