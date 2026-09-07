# [H] Unescaped parameters in the PostgreSQL JDBC driver

## Summary
Severity: High
Advisory: GHSA-h86w-m5rm-xr33
CVE: CVE-2012-1618
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h86w-m5rm-xr33
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=0 <8.2

## Details
Interaction error in the PostgreSQL JDBC driver before 8.2, when used with a PostgreSQL server with the "standard_conforming_strings" option enabled, such as the default configuration of PostgreSQL 9.1, does not properly escape unspecified JDBC statement parameters, which allows remote attackers to perform SQL injection attacks.  NOTE: as of 20120330, it was claimed that the upstream developer planned to dispute this issue, but an official dispute has not been posted as of 20121005.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1618
- https://bugzilla.novell.com/show_bug.cgi?id=754273
- https://github.com/pgjdbc/pgjdbc
- http://archives.neohapsis.com/archives/bugtraq/2012-03/0126.html
- http://lists.opensuse.org/opensuse-security/2012-03/msg00024.html
- http://www.openwall.com/lists/oss-security/2012/03/30/8
- http://www.openwall.com/lists/oss-security/2012/03/30/9
- http://www.openwall.com/lists/oss-security/2012/03/31/1
- http://www.openwall.com/lists/oss-security/2012/04/02/4
- http://www.openwall.com/lists/oss-security/2012/04/04/11
- http://www.openwall.com/lists/oss-security/2012/04/04/4
- http://www.openwall.com/lists/oss-security/2012/04/04/5
- http://www.openwall.com/lists/oss-security/2012/04/04/9
- http://www.osvdb.org/80641
