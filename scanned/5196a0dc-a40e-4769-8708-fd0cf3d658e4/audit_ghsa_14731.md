# [C] Craft CMS has potential RCE when PHP `register_argc_argv` config setting is enabled

## Summary
Severity: Critical
Advisory: GHSA-2p6p-9rc9-62j9
CVE: CVE-2024-56145
CWE: CWE-78, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-2p6p-9rc9-62j9
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.5.2
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.13.2
- Packagist: `craftcms/cms` — affected >=3.0.0 <3.9.14

## Details
### Impact
You are affected if your php.ini configuration has `register_argc_argv` enabled.

### Patches
Update to 3.9.14, 4.13.2, or 5.5.2.

### Workarounds
If you can't upgrade yet, and `register_argc_argv` is enabled, you can disable it to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-2p6p-9rc9-62j9
- https://nvd.nist.gov/vuln/detail/CVE-2024-56145
- https://github.com/craftcms/cms/commit/82e893fb794d30563da296bca31379c0df0079b3
- https://github.com/Chocapikk/CVE-2024-56145
- https://github.com/craftcms/cms
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-56145
