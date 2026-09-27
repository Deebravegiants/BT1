# [H] ALPINE-CVE-2019-17346

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17346
Ecosystem: Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17346
Type: osv

## Affected
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r0

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges because of an incompatibility between Process Context Identifiers (PCID) and TLB flushes.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17346
