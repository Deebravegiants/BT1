# [M] Apache Log4j Core: `verifyHostName` attribute silently ignored in TLS configuration

## Summary
Severity: Medium
Advisory: GHSA-6hg6-v5c8-fphq
CVE: CVE-2026-34477
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-6hg6-v5c8-fphq
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.12.0 <2.25.4
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=3.0.0-alpha1

## Details
The fix for  CVE-2025-68161 was incomplete: it addressed hostname verification only when enabled via the  [`log4j2.sslVerifyHostName`](https://logging.apache.org/log4j/2.x/manual/systemproperties.html#log4j2.sslVerifyHostName) system property, but not when configured through the [`verifyHostName`](https://logging.apache.org/log4j/2.x/manual/appenders/network.html#SslConfiguration-attr-verifyHostName) attribute of the `<Ssl>` element.

Although the `verifyHostName` configuration attribute was introduced in Log4j Core 2.12.0, it was silently ignored in all versions through 2.25.3, leaving TLS connections vulnerable to interception regardless of the configured value.

A network-based attacker may be able to perform a man-in-the-middle attack when all of the following conditions are met:

  *  An SMTP, Socket, or Syslog appender is in use.
  *  TLS is configured via a nested <Ssl> element.
  *  The attacker can present a certificate issued by a CA trusted by the appender's configured trust store, or by the default Java trust store if none is configured.

This issue does not affect users of the HTTP appender, which uses a separate [`verifyHostname`](https://logging.apache.org/log4j/2.x/manual/appenders/network.html#HttpAppender-attr-verifyHostName) attribute that was not subject to this bug and verifies host names by default.

Users are advised to upgrade to Apache Log4j Core 2.25.4, which corrects this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34477
- https://github.com/apache/logging-log4j2/pull/4075
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/lkx8cl46t2bvkcwfcb2pd43ygc097lq4
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/manual/appenders/network.html#SslConfiguration-attr-verifyHostName
- https://logging.apache.org/security.html#CVE-2026-34477
