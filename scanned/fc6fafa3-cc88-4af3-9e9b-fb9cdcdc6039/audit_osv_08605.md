# [H] CVE-2016-4574

## Summary
Severity: High
Advisory: CVE-2016-4574
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4574
Type: osv

## Details
Off-by-one error in the append_utf8_value function in the DN decoder (dn.c) in Libksba before 1.3.4 allows remote attackers to cause a denial of service (out-of-bounds read) via invalid utf-8 encoded data. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-4356.

## References
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=libksba.git%3Ba=commit%3Bh=6be61daac047d8e6aa941eb103f8e71a1d4e3c75
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00087.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00028.html
- http://www.openwall.com/lists/oss-security/2016/05/10/3
- http://www.openwall.com/lists/oss-security/2016/05/10/4
- http://www.ubuntu.com/usn/USN-2982-1
