# [H] CVE-2018-18883

## Summary
Severity: High
Advisory: CVE-2018-18883
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2018-18883
Type: osv

## Details
An issue was discovered in Xen 4.9.x through 4.11.x, on Intel x86 platforms, allowing x86 HVM and PVH guests to cause a host OS denial of service (NULL pointer dereference) or possibly have unspecified other impact because nested VT-x is not properly restricted.

## References
- http://www.securityfocus.com/bid/105817
- http://www.securitytracker.com/id/1042021
- https://xenbits.xen.org/xsa/advisory-278.html
