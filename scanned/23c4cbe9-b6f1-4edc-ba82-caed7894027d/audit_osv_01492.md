# [H] ALPINE-CVE-2019-17341

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17341
Ecosystem: Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17341
Type: osv

## Affected
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r0

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges by leveraging a page-writability race condition during addition of a passed-through PCI device.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17341
