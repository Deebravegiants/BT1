# [C] Server-Side Request Forgery and Uncontrolled Resource Consumption in LemMinX

## Summary
Severity: Critical
Advisory: GHSA-52vv-3vf7-f7wh
CVE: CVE-2022-0671
CWE: CWE-400, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-52vv-3vf7-f7wh
Type: github-advisory

## Affected
- Maven: `org.eclipse.lemminx:lemminx-parent` — affected >=0 <0.19.0

## Details
A flaw was found in vscode-xml in versions prior to 0.19.0. Schema download could lead to blind SSRF or DoS via a large file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0671
- https://github.com/eclipse/lemminx/issues/1169
- https://github.com/eclipse/lemminx
- https://github.com/eclipse/lemminx/blob/master/CHANGELOG.md#0190-february-14-2022
- https://github.com/redhat-developer/vscode-xml/blob/master/CHANGELOG.md#0190-february-14-2022
