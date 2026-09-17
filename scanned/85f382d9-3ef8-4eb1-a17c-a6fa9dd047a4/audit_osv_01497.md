# [M] ALPINE-CVE-2019-17348

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-17348
Ecosystem: Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17348
Type: osv

## Affected
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r0

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service because of an incompatibility between Process Context Identifiers (PCID) and shadow-pagetable switching.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17348
