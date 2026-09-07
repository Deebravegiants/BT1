# [M] DOM-XSS on Backoffice login screen.

## Summary
Severity: Medium
Advisory: GHSA-v98m-398x-269r
CVE: CVE-2023-48313
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-v98m-398x-269r
Type: github-advisory

## Affected
- NuGet: `Umbraco.CMS` — affected >=10.0.0 <10.8.1
- NuGet: `Umbraco.CMS` — affected >=11.0.0 <12.3.4

## Details
#### Impact
Cross-site scripting (XSS) enable attackers to bring malicious content into a website or application.

#### Explanation of the vulnerability 

A DOM-XSS can be exploited when users are successfully logging into the Backoffice.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-v98m-398x-269r
- https://nvd.nist.gov/vuln/detail/CVE-2023-48313
- https://github.com/umbraco/Umbraco-CMS
