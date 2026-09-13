# [M] CVE-2018-19964

## Summary
Severity: Medium
Advisory: CVE-2018-19964
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/CVE-2018-19964
Type: osv

## Details
An issue was discovered in Xen 4.11.x allowing x86 guest OS users to cause a denial of service (host OS hang) because the p2m lock remains unavailable indefinitely in certain error conditions.

## References
- http://www.securityfocus.com/bid/106182
- https://xenbits.xen.org/xsa/advisory-277.html
