# [M] Apache Log4net: Silent log event loss in XmlLayout and XmlLayoutSchemaLog4J due to unescaped XML 1.0 forbidden characters

## Summary
Severity: Medium
Advisory: GHSA-4f7c-pmjv-c25w
CVE: CVE-2026-40021
CWE: CWE-116
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-4f7c-pmjv-c25w
Type: github-advisory

## Affected
- NuGet: `log4net` — affected >=0 <3.3.0

## Details
Apache Log4net's  XmlLayout https://logging.apache.org/log4net/manual/configuration/layouts.html#layout-list  and  XmlLayoutSchemaLog4J https://logging.apache.org/log4net/manual/configuration/layouts.html#layout-list , in versions before 3.3.0, fail to sanitize characters forbidden by the  XML 1.0 specification https://www.w3.org/TR/xml/#charsets  in MDC property keys and values, as well as the identity field that may carry attacker-influenced data. This causes an exception during serialization and the silent loss of the affected log event.

An attacker who can influence any of these fields can exploit this to suppress individual log records, impairing audit trails and detection of malicious activity.

Users are advised to upgrade to Apache Log4net 3.3.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40021
- https://github.com/apache/logging-log4net/pull/280
- https://github.com/apache/logging-log4net
- https://lists.apache.org/thread/q8otftjswhk69n3kxslqg7cobr0x4st7
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4net/manual/configuration/layouts.html
- https://logging.apache.org/security.html#CVE-2026-40021
- http://www.openwall.com/lists/oss-security/2026/04/10/11
