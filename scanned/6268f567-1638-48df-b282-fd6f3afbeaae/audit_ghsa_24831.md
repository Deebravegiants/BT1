# [H] Deserialization of Untrusted Data in Apache Brooklyn

## Summary
Severity: High
Advisory: GHSA-9cqh-5x6g-wgm9
CVE: CVE-2016-8744
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9cqh-5x6g-wgm9
Type: github-advisory

## Affected
- Maven: `org.apache.brooklyn:brooklyn` — affected >=0 <0.10.0

## Details
Apache Brooklyn uses the SnakeYAML library for parsing YAML inputs. SnakeYAML allows the use of YAML tags to indicate that SnakeYAML should unmarshal data to a Java type. In the default configuration in Brooklyn before 0.10.0, SnakeYAML will allow unmarshalling to any Java type available on the classpath. This could provide an authenticated user with a means to cause the JVM running Brooklyn to load and run Java code without detection by Brooklyn. Such code would have the privileges of the Java process running Brooklyn, including the ability to open files and network connections, and execute system commands. There is known to be a proof-of-concept exploit using this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8744
- https://brooklyn.apache.org/community/security/CVE-2016-8744.html
- https://lists.apache.org/thread.html/3f4d09c1c1a3cdfd1da0a05c8362769b917c078eed5b6c2f8e37a761@%3Cdev.brooklyn.apache.org%3E
