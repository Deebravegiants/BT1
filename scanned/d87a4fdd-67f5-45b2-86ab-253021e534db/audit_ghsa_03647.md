# [C] Credential exposure through log files in Undertow

## Summary
Severity: Critical
Advisory: GHSA-jwgx-9mmh-684w
CVE: CVE-2019-3888
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-jwgx-9mmh-684w
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.21

## Details
A vulnerability was found in Undertow web server before 2.0.21. An information exposure of plain text credentials through log files because Connectors.executeRootHandler:402 logs the HttpServerExchange object at ERROR level using UndertowLogger.REQUEST_LOGGER.undertowRequestFailed(t, exchange)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3888
- https://access.redhat.com/errata/RHSA-2019:2439
- https://access.redhat.com/errata/RHSA-2019:2998
- https://access.redhat.com/errata/RHSA-2020:0727
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3888
- https://security.netapp.com/advisory/ntap-20220210-0019
- http://www.securityfocus.com/bid/108739
