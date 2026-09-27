# [M] Apache Log4j Core: Silent log event loss in XmlLayout due to unescaped XML 1.0 forbidden characters

## Summary
Severity: Medium
Advisory: GHSA-3pxv-7cmr-fjr4
CVE: CVE-2026-34480
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-3pxv-7cmr-fjr4
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.0-alpha1 <2.25.4
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=3.0.0-alpha1

## Details
Apache Log4j Core's [`XmlLayout`](https://logging.apache.org/log4j/2.x/manual/layouts.html#XmlLayout), in versions up to and including 2.25.3, fails to sanitize characters forbidden by the [XML 1.0 specification](https://www.w3.org/TR/xml/#charsets), producing invalid XML output whenever a log message or MDC value contains such characters.

The impact depends on the StAX implementation in use:

  *  **JRE built-in StAX**: Forbidden characters are silently written to the output, producing malformed XML. Conforming parsers must reject such documents with a fatal error, which may cause downstream log-processing systems to drop the affected records.
  *  **Alternative StAX implementations** (e.g., [Woodstox](https://github.com/FasterXML/woodstox), a transitive dependency of the Jackson XML Dataformat module): An exception is thrown during the logging call, and the log event is never delivered to its intended appender, only to Log4j's internal status logger.

Users are advised to upgrade to Apache Log4j Core 2.25.4, which corrects this issue by sanitizing forbidden characters before XML output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34480
- https://github.com/apache/logging-log4j2/pull/4077
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/5x0hcnng0chhghp6jgjdp3qmbbhfjzhb
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/manual/layouts.html#XmlLayout
- https://logging.apache.org/security.html#CVE-2026-34480
- http://www.openwall.com/lists/oss-security/2026/04/10/9
