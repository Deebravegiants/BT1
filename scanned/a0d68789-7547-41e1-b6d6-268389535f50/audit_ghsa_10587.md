# [M] Apache Log4j Core: log injection in `Rfc5424Layout` due to silent configuration incompatibility

## Summary
Severity: Medium
Advisory: GHSA-445c-vh5m-36rj
CVE: CVE-2026-34478
CWE: CWE-117, CWE-684
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-445c-vh5m-36rj
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.21.0 <2.25.4
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=3.0.0-beta1

## Details
Apache Log4j Core's [`Rfc5424Layout`](https://logging.apache.org/log4j/2.x/manual/layouts.html#RFC5424Layout), in versions 2.21.0 through 2.25.3, is vulnerable to log injection via CRLF sequences due to undocumented renames of security-relevant configuration attributes.

Two distinct issues affect users of stream-based syslog services who configure Rfc5424Layout directly:

  *  The `newLineEscape` attribute was silently renamed, causing newline escaping to stop working for users of TCP framing (RFC 6587), exposing them to CRLF injection in log output.
  *  The `useTlsMessageFormat` attribute was silently renamed, causing users of TLS framing (RFC 5425) to be silently downgraded to unframed TCP (RFC 6587), without newline escaping.

Users of the `SyslogAppender` are not affected, as its configuration attributes were not modified.

Users are advised to upgrade to Apache Log4j Core 2.25.4, which corrects this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34478
- https://github.com/apache/logging-log4j2/pull/4074
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/3k1clr2l6vkdnl4cbhjrnt1nyjvb5gwt
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/manual/layouts.html#RFC5424Layout
- https://logging.apache.org/security.html#CVE-2026-34478
- http://www.openwall.com/lists/oss-security/2026/04/10/7
