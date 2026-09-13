# [M] Privilege Escalation using Spoofing

## Summary
Severity: Medium
Advisory: GHSA-cfr5-7p54-4qg8
CVE: CVE-2023-49273
CWE: CWE-863
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-cfr5-7p54-4qg8
Type: github-advisory

## Affected
- NuGet: `Umbraco.CMS` — affected >=8.0.0 <8.18.10
- NuGet: `Umbraco.CMS` — affected >=9.0.0 <10.8.1
- NuGet: `Umbraco.CMS` — affected >=11.0.0 <12.3.4

## Details
#### Impact
Users with low privileges ( Editor, etc) are able to access some unintended endpoints.

#### Explanation of the vulnerability 
Possible to delete redirect urls, when disabled by admin with only access to backoffice
Possible to access the examine dashboard with only access to backoffice
Possible to access the published cache dashboard with only access to backoffice
Possible to access the telemetry dashboard with only access to backoffice
Possible to access the languages with only access to backoffice
Possible to access the stylesheets with only access to backoffice

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-cfr5-7p54-4qg8
- https://nvd.nist.gov/vuln/detail/CVE-2023-49273
- https://github.com/umbraco/Umbraco-CMS
