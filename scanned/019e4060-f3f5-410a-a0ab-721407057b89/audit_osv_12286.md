# [H] CVE-2018-1123

## Summary
Severity: High
Advisory: CVE-2018-1123
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1123
Type: osv

## Details
procps-ng before version 3.3.15 is vulnerable to a denial of service in ps via mmap buffer overflow. Inbuilt protection in ps maps a guard page at the end of the overflowed buffer, ensuring that the impact of this flaw is limited to a crash (temporary denial of service).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00059.html
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://seclists.org/oss-sec/2018/q2/122
- http://www.securityfocus.com/bid/104214
- https://lists.debian.org/debian-lts-announce/2018/05/msg00021.html
- https://security.gentoo.org/glsa/201805-14
- https://usn.ubuntu.com/3658-1/
- https://usn.ubuntu.com/3658-3/
- https://www.debian.org/security/2018/dsa-4208
- https://www.exploit-db.com/exploits/44806/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1123
- https://www.qualys.com/2018/05/17/procps-ng-audit-report-advisory.txt
