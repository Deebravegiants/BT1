# [H] CVE-2015-8948

## Summary
Severity: High
Advisory: CVE-2015-8948
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/CVE-2015-8948
Type: osv

## Details
idn in GNU libidn before 1.33 might allow remote attackers to obtain sensitive memory information by reading a zero byte as input, which triggers an out-of-bounds read.

## References
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00005.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00098.html
- http://www.debian.org/security/2016/dsa-3658
- http://www.openwall.com/lists/oss-security/2016/07/20/6
- http://www.openwall.com/lists/oss-security/2016/07/21/4
- http://www.securityfocus.com/bid/92070
- http://www.ubuntu.com/usn/USN-3068-1
- https://lists.gnu.org/archive/html/help-libidn/2016-07/msg00009.html
- http://www.openwall.com/lists/oss-security/2016/07/20/6
- http://www.openwall.com/lists/oss-security/2016/07/21/4
- http://git.savannah.gnu.org/cgit/libidn.git/commit/?id=570e68886c41c2e765e6218cb317d9a9a447a041
- http://git.savannah.gnu.org/cgit/libidn.git/commit/?id=570e68886c41c2e765e6218cb317d9a9a447a041
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
