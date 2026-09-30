# [M] CVE-2016-6153

## Summary
Severity: Medium
Advisory: CVE-2016-6153
CVSS: 5.9 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6153
Type: osv

## Details
os_unix.c in SQLite before 3.13.0 improperly implements the temporary directory search algorithm, which might allow local users to obtain sensitive information, cause a denial of service (application crash), or have unspecified other impact by leveraging use of the current working directory for temporary files.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IGQTH7V45QVHFDXJAEECHEO3HHD644WZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU4NZ6DDU4BEM3ACM3FM6GLEPX56ZQXK/
- https://usn.ubuntu.com/4019-1/
- https://usn.ubuntu.com/4019-2/
- https://www.tenable.com/security/tns-2016-20
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00053.html
- http://www.openwall.com/lists/oss-security/2016/07/01/2
- http://www.securityfocus.com/bid/91546
- http://www.sqlite.org/cgi/src/info/67985761aa93fb61
- https://www.korelogic.com/Resources/Advisories/KL-001-2016-003.txt
- https://www.sqlite.org/releaselog/3_13_0.html
- http://www.openwall.com/lists/oss-security/2016/07/01/1
