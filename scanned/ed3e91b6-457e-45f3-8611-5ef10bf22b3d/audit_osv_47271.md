# [M] CVE-2016-2037

## Summary
Severity: Medium
Advisory: CVE-2016-2037
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-22
Source: https://osv.dev/vulnerability/CVE-2016-2037
Type: osv

## Details
The cpio_safer_name_suffix function in util.c in cpio 2.11 allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted cpio file.

## References
- http://www.openwall.com/lists/oss-security/2016/01/19/4
- http://www.openwall.com/lists/oss-security/2016/01/22/4
- http://www.securityfocus.com/bid/82293
- http://www.securitytracker.com/id/1035067
- http://www.debian.org/security/2016/dsa-3483
- http://www.ubuntu.com/usn/USN-2906-1
