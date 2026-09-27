# [M] Improper Access Control in Telerik Extensions

## Summary
Severity: Medium
Advisory: GHSA-8h7p-qjv8-9mp4
CVE: CVE-2018-17060
CWE: CWE-284
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8h7p-qjv8-9mp4
Type: github-advisory

## Affected
- NuGet: `TelerikMvcExtensions` — affected >=0

## Details
Telerik Extensions for ASP.NET MVC (all versions) does not whitelist requests, which can allow a remote attacker to access files inside the server's web directory.  NOTE: this product has been obsolete since June 2013.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17060
- https://www.telerik.com/support/code-library/security-alert-for-the-obsolete-telerik-extensions-for-asp-net-mvc
