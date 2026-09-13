# [H] CVE-2020-14295

## Summary
Severity: High
Advisory: CVE-2020-14295
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-14295
Type: osv

## Details
A SQL injection issue in color.php in Cacti 1.2.12 allows an admin to inject SQL via the filter parameter. This can lead to remote command execution because the product accepts stacked queries.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00085.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W64CIB6L4HZRVQSWKPDDKXJO4J2XTOXD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZKM5G3YNSZDHDZMPCMAHG5B5M2V4XYSE/
- https://security.gentoo.org/glsa/202007-03
- https://github.com/Cacti/cacti/issues/3622
- http://packetstormsecurity.com/files/162384/Cacti-1.2.12-SQL-Injection-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/162918/Cacti-1.2.12-SQL-Injection-Remote-Command-Execution.html
