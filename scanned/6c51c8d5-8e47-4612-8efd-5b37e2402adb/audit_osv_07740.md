# [H] Apache Tomcat: DoS via WebSocket chat example

## Summary
Severity: High
Advisory: BIT-tomcat-2026-66299
Aliases: CVE-2026-66299
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-66299
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Uncontrolled Resource Consumption vulnerability in Apache Tomcat's WebSocket chat example.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.24 through 10.1.57, from 9.0.89 through 9.0.120. Users who have followed the security guidance to remove the examples web application are not affected by this issue.

Users are recommended to remove the examples web application or to upgrade to version 11.0.25, 10.1.58 or 9.0.121 (when released), which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/28/25
- https://lists.apache.org/thread/8owczcc1o8qw1rxmg9gvfk4w2jnh4l5k
- https://nvd.nist.gov/vuln/detail/CVE-2026-66299
