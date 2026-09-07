# [M] Umbraco CMS contains a server-side request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h66j-xm43-47pp
CVE: CVE-2021-47776
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-h66j-xm43-47pp
Type: github-advisory

## Affected
- NuGet: `UmbracoCms` — affected 8.14.1

## Details
Umbraco CMS v8.14.1 contains a server-side request forgery vulnerability that allows attackers to manipulate baseUrl parameters in multiple dashboard and help controller endpoints. Attackers can craft malicious requests to the GetContextHelpForPage, GetRemoteDashboardContent, and GetRemoteDashboardCss endpoints to trigger unauthorized server-side requests to external hosts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-47776
- https://github.com/umbraco/Umbraco-CMS
- https://our.umbraco.com
- https://releases.umbraco.com/all-releases
- https://www.exploit-db.com/exploits/50462
