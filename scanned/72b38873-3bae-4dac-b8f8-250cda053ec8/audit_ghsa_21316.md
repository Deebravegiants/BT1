# [C] HyperSQL DataBase vulnerable to remote code execution when processing untrusted input

## Summary
Severity: Critical
Advisory: GHSA-77xx-rxvh-q682
CVE: CVE-2022-41853
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-77xx-rxvh-q682
Type: github-advisory

## Affected
- Maven: `org.hsqldb:hsqldb` — affected >=0 <2.7.1

## Details
Those using `java.sql.Statement` or `java.sql.PreparedStatement` in hsqldb (HyperSQL DataBase) to process untrusted input may be vulnerable to a remote code execution attack. By default it is allowed to call any static method of any Java class in the classpath resulting in code execution. The issue can be prevented by updating to 2.7.1 or by setting the system property "hsqldb.method_class_names" to classes which are allowed to be called. For example, `System.setProperty("hsqldb.method_class_names", "abc")` or Java argument `-Dhsqldb.method_class_names="abc"` can be used. From version 2.7.1 all classes by default are not accessible except those in `java.lang.Math` and need to be manually enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41853
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=50212#c7
- https://lists.debian.org/debian-lts-announce/2022/12/msg00020.html
- https://sourceforge.net/projects/hsqldb
- https://www.debian.org/security/2023/dsa-5313
- http://hsqldb.org/doc/2.0/guide/sqlroutines-chapt.html#src_jrt_access_control
