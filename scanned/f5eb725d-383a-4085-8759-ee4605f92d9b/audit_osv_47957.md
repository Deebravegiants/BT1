# [M] CVE-2017-15591

## Summary
Severity: Medium
Advisory: CVE-2017-15591
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15591
Type: osv

## Details
An issue was discovered in Xen 4.5.x through 4.9.x allowing attackers (who control a stub domain kernel or tool stack) to cause a denial of service (host OS crash) because of a missing comparison (of range start to range end) within the DMOP map/unmap implementation.

## References
- https://security.gentoo.org/glsa/201801-14
- https://xenbits.xen.org/xsa/advisory-238.html
