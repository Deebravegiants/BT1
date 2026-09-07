# [M] Umbraco Workflow's Backoffice users can execute arbitrary SQL

## Summary
Severity: Medium
Advisory: GHSA-287f-46j7-j4wh
CVE: CVE-2024-32872
CWE: CWE-89
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-287f-46j7-j4wh
Type: github-advisory

## Affected
- NuGet: `Umbraco.Workflow` — affected >=0 <10.3.9
- NuGet: `Umbraco.Workflow` — affected >=11.0.0-rc1 <12.2.6
- NuGet: `Umbraco.Workflow` — affected >=13.0.0-rc1 <13.0.6
- NuGet: `Plumber.Workflow` — affected >=0 <10.1.2

## Details
### Impact

Backoffice users can execute arbitrary SQL.

### Explanation of the vulnerability
A Backoffice user can modify requests to a particular API endpoint to include SQL which will be executed by the server.

### Affected versions 
All versions

### Patches

Workflow 10.3.9, 12.2.6, 13.0.6, Plumber 10.1.2

### References
[Upgrading Umbraco Workflow](https://docs.umbraco.com/umbraco-workflow/upgrading/upgrading)

## References
- https://github.com/umbraco/Umbraco.Workflow.Issues/security/advisories/GHSA-287f-46j7-j4wh
- https://nvd.nist.gov/vuln/detail/CVE-2024-32872
