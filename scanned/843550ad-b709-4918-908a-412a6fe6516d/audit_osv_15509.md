# [C] CVE-2019-16928

## Summary
Severity: Critical
Advisory: CVE-2019-16928
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-16928
Type: osv

## Details
Exim 4.92 through 4.92.2 allows remote code execution, a different vulnerability than CVE-2019-15846. There is a heap-based buffer overflow in string_vformat in string.c involving a long EHLO command.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-16928
- http://www.openwall.com/lists/oss-security/2019/09/28/3
- http://www.openwall.com/lists/oss-security/2019/09/28/4
- https://lists.exim.org/lurker/message/20190927.032457.c1044d4c.en.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EED7HM3MFIBAP5OIMJAFJ35JAJABTVSC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T3TJW4HPYH3O5HZCWGD6NSHTEBTTAPDC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UY6HPRW7MR3KBQ5JFHH6OXM7YCZBJCOB/
- https://seclists.org/bugtraq/2019/Sep/60
- https://security.gentoo.org/glsa/202003-47
- https://usn.ubuntu.com/4141-1/
- https://www.debian.org/security/2019/dsa-4536
- https://bugs.exim.org/show_bug.cgi?id=2449
- https://git.exim.org/exim.git/commit/478effbfd9c3cc5a627fc671d4bf94d13670d65f
- http://www.openwall.com/lists/oss-security/2019/09/28/1
- http://www.openwall.com/lists/oss-security/2019/09/28/2
