# [M] CVE-2016-4963

## Summary
Severity: Medium
Advisory: CVE-2016-4963
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2016-4963
Type: osv

## Details
The libxl device-handling in Xen through 4.6.x allows local guest OS users with access to the driver domain to cause a denial of service (management tool confusion) by manipulating information in the backend directories in xenstore.

## References
- http://www.securitytracker.com/id/1036024
- https://lists.debian.org/debian-lts-announce/2018/09/msg00006.html
- http://xenbits.xen.org/xsa/advisory-178.html
