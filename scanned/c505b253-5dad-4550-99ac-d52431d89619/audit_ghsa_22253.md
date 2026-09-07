# [M] Ignite Realtime Openfire allows Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-h2mq-p9r5-wh94
CVE: CVE-2019-20525
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h2mq-p9r5-wh94
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <4.4.2

## Details
Ignite Realtime Openfire 4.4.1 allows XSS via the setup/setup-datasource-standard.jsp driver parameter. This issue was fixed in version 4.4.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20525
- https://www.netsparker.com/web-applications-advisories/ns-19-015-reflected-cross-site-scripting-in-openfire
