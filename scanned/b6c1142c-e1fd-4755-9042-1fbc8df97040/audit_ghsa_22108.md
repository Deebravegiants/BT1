# [M] Cross-site Scripting in Graylog Server

## Summary
Severity: Medium
Advisory: GHSA-h7g4-65mf-6mxh
CVE: CVE-2018-11650
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h7g4-65mf-6mxh
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=0 <2.4.4

## Details
Graylog before v2.4.4 has an XSS security issue with unescaped text in notifications, related to toastr and util/UserNotification.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11650
- https://github.com/Graylog2/graylog2-server/pull/4727
- https://github.com/Graylog2/graylog2-server
- https://www.graylog.org/post/announcing-graylog-v2-4-4
