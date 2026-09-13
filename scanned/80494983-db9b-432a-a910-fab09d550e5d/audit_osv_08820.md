# [H] CVE-2016-6261

## Summary
Severity: High
Advisory: CVE-2016-6261
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/CVE-2016-6261
Type: osv

## Details
The idna_to_ascii_4i function in lib/idna.c in libidn before 1.33 allows context-dependent attackers to cause a denial of service (out-of-bounds read and crash) via 64 bytes of input.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00098.html
- http://www.debian.org/security/2016/dsa-3658
- http://www.openwall.com/lists/oss-security/2016/07/20/6
- http://www.openwall.com/lists/oss-security/2016/07/21/4
- http://www.securityfocus.com/bid/92070
- http://www.ubuntu.com/usn/USN-3068-1
- https://lists.gnu.org/archive/html/help-libidn/2015-07/msg00016.html
- https://lists.gnu.org/archive/html/help-libidn/2016-07/msg00009.html
- http://git.savannah.gnu.org/cgit/libidn.git/commit/?id=f20ce1128fb7f4d33297eee307dddaf0f92ac72d
