# [M] Apache Log4j JSON Template Layout: Improper serialization of non-finite floating-point values in JsonTemplateLayout

## Summary
Severity: Medium
Advisory: GHSA-w35j-pv5h-q9q9
CVE: CVE-2026-34481
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-w35j-pv5h-q9q9
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-layout-template-json` — affected >=2.14.0 <2.25.4
- Maven: `org.apache.logging.log4j:log4j-layout-template-json` — affected >=3.0.0-alpha1

## Details
Apache Log4j's [`JsonTemplateLayout`](https://logging.apache.org/log4j/2.x/manual/json-template-layout.html), in versions up to and including 2.25.3, produces invalid JSON output when log events contain non-finite floating-point values (`NaN`, `Infinity`, or `-Infinity`), which are prohibited by RFC 8259. This may cause downstream log processing systems to reject or fail to index affected records.

An attacker can exploit this issue only if both of the following conditions are met:

  *  The application uses `JsonTemplateLayout`.
  *  The application logs a `MapMessage` containing an attacker-controlled floating-point value.

Users are advised to upgrade to Apache Log4j JSON Template Layout 2.25.4, which corrects this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34481
- https://github.com/apache/logging-log4j2/pull/4080
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/n34zdv00gbkdbzt2rx9rf5mqz6lhopcv
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/manual/json-template-layout.html
- https://logging.apache.org/security.html#CVE-2026-34481
- http://www.openwall.com/lists/oss-security/2026/04/10/10
