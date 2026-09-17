# [M] ALPINE-CVE-2019-17345

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-17345
Ecosystem: Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17345
Type: osv

## Affected
- Alpine:v3.9: `xen` — affected >=4.8.0 <4.11.2-r0

## Details
An issue was discovered in Xen 4.8.x through 4.11.x allowing x86 PV guest OS users to cause a denial of service because mishandling of failed IOMMU operations causes a bug check during the cleanup of a crashed guest.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17345
