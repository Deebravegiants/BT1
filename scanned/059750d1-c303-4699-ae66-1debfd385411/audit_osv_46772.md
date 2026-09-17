# [M] CVE-2015-2060

## Summary
Severity: Medium
Advisory: CVE-2015-2060
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2015-2060
Type: osv

## Details
cabextract before 1.6 does not properly check for leading slashes when extracting files, which allows remote attackers to conduct absolute directory traversal attacks via a malformed UTF-8 character that is changed to a UTF-8 encoded slash.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151145.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151147.html
- http://www.cabextract.org.uk/
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:064
- http://www.openwall.com/lists/oss-security/2015/02/18/3
- http://www.openwall.com/lists/oss-security/2015/02/23/16
- http://www.openwall.com/lists/oss-security/2015/02/23/24
- http://www.openwall.com/lists/oss-security/2015/02/18/3
- http://www.openwall.com/lists/oss-security/2015/02/23/16
- http://www.openwall.com/lists/oss-security/2015/02/23/24
- http://www.openwall.com/lists/oss-security/2015/02/18/3
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151145.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151147.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151145.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151147.html
- http://www.openwall.com/lists/oss-security/2015/02/23/16
- http://www.openwall.com/lists/oss-security/2015/02/23/24
