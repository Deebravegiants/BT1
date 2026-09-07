# [M] formwork Cross-site scripting vulnerability in Markdown fields

## Summary
Severity: Medium
Advisory: GHSA-gx8m-f3mp-fg99
CVE: CVE-2024-35621
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-gx8m-f3mp-fg99
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=0 <1.13.0

## Details
### Impact
Users with access to the administration panel with page editing permissions could insert `<script>` tags in markdown fields, which are exposed on the publicly accessible site pages, leading to potential XSS injections.

### Patches

- [**Formwork 1.13.0**](https://github.com/getformwork/formwork/releases/tag/1.13.0) has been released with a patch that solves this vulnerability. Now the system config option `content.safe_mode` (enabled by default) controls whether HTML tags and potentially dangerous links are escaped. This is configurable as in some cases more flexibility should be given. Panel users should be only a controlled group of editors, which cannot enable the option by themselves, and not a generic group. This mitigates the chance of introducing vulnerabilities.
- [**Formwork 2.x** (6adc302)](https://github.com/getformwork/formwork/commit/6adc302f5a294f2ffbbf1571dd4ffea6b7876723) adds a similar `content.safeMode` system option. Like Formwork 1.13.0, by default HTML tags and dangerous link are escaped. Even if enabled by an administrator, however, `<script>` and other dangerous tags are still converted to text, but secure tags are allowed.

### References
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-35621

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-gx8m-f3mp-fg99
- https://nvd.nist.gov/vuln/detail/CVE-2024-35621
- https://github.com/getformwork/formwork/commit/2d92e6dbf99a9a49797947afbda0cdd4e56e11df
- https://github.com/getformwork/formwork/commit/6adc302f5a294f2ffbbf1571dd4ffea6b7876723
- https://github.com/getformwork/formwork
