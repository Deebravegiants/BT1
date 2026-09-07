# [M] Umbraco Forms's Short and Long Answer Fields Are Not Validated Server-Side For Maximum Length

## Summary
Severity: Medium
Advisory: GHSA-9v8m-qv22-f268
CVE: CVE-2025-23041
CWE: CWE-20, CWE-602
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-9v8m-qv22-f268
Type: github-advisory

## Affected
- NuGet: `Umbraco.Forms` — affected >=0 <10.5.7
- NuGet: `UmbracoForms` — affected >=0 <8.13.16
- NuGet: `Umbraco.Forms` — affected >=11.0.0-rc1 <13.2.2
- NuGet: `Umbraco.Forms` — affected >=14.0.0-beta001 <14.1.2

## Details
### Impact

Character limits configured by editors for short and long answer fields are validated only client-side, not server-side.

### Patches

Patched in 8.13.16, 10.5.7, 13.2.2, 14.1.2

## References
- https://github.com/umbraco/Umbraco.Forms.Issues/security/advisories/GHSA-9v8m-qv22-f268
- https://nvd.nist.gov/vuln/detail/CVE-2025-23041
