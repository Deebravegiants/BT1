# [M] CVE-2016-3961

## Summary
Severity: Medium
Advisory: CVE-2016-3961
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-15
Source: https://osv.dev/vulnerability/CVE-2016-3961
Type: osv

## Details
Xen and the Linux kernel through 4.5.x do not properly suppress hugetlbfs support in x86 PV guests, which allows local PV guest OS users to cause a denial of service (guest OS crash) by attempting to access a hugetlbfs mapped area.

## References
- http://www.securityfocus.com/bid/86068
- http://www.ubuntu.com/usn/USN-3003-1
- http://www.ubuntu.com/usn/USN-3004-1
- http://www.ubuntu.com/usn/USN-3005-1
- http://www.ubuntu.com/usn/USN-3006-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.securitytracker.com/id/1035569
- http://www.ubuntu.com/usn/USN-3002-1
- http://www.ubuntu.com/usn/USN-3007-1
- http://www.ubuntu.com/usn/USN-3049-1
- http://www.ubuntu.com/usn/USN-3050-1
- http://xenbits.xen.org/xsa/advisory-174.html
- http://www.ubuntu.com/usn/USN-3001-1
- http://xenbits.xen.org/xsa/xsa174.patch
