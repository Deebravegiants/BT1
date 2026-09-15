# [H] Insecure defaults in UmbracoForms

## Summary
Severity: High
Advisory: GHSA-8m73-w2r2-6xxj
CVE: CVE-2020-7685
CWE: CWE-1188
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-8m73-w2r2-6xxj
Type: github-advisory

## Affected
- NuGet: `UmbracoForms` — affected >=0

## Details
This affects all versions of package UmbracoForms. When using the default configuration for upload forms, it is possible to upload arbitrary file types. The package offers a way for users to mitigate the issue. The users of this package can create a custom workflow and frontend validation that blocks certain file types, depending on their security needs and policies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7685
- https://snyk.io/vuln/SNYK-DOTNET-UMBRACOFORMS-595765
