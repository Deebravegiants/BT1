# [M] Umbraco.Cms: XSS/HTML Injection in Umbraco Backoffice confirmation dialog

## Summary
Severity: Medium
Advisory: GHSA-vr9v-27gg-qgx4
CVE: CVE-2026-46609
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-vr9v-27gg-qgx4
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <17.4.0

## Details
### Impact
Authenticated users are able to inject HTML vulnerability into an input field, which is rendered in the confirmation dialog without proper output encoding.

### Patches
This issue has been patched in 17.4.0

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-vr9v-27gg-qgx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-46609
- https://github.com/umbraco/Umbraco-CMS
