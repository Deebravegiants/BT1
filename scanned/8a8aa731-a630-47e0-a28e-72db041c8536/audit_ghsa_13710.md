# [H] Statamic CMS vulnerable to remote code execution via form uploads

## Summary
Severity: High
Advisory: GHSA-2r53-9295-3m86
CVE: CVE-2023-48217
CWE: CWE-434, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-2r53-9295-3m86
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=4.0.0 <4.34.0
- Packagist: `statamic/cms` — affected >=0 <3.4.14

## Details
### Impact

Similar to [another advisory](https://github.com/statamic/cms/security/advisories/GHSA-72hg-5wr5-rmfc), certain additional PHP files crafted to look like images may be uploaded regardless of mime type validation rules. This affects front-end forms using the "Forms" feature, and asset upload fields in the control panel.

### Patches
It has been patched in 3.4.14 and 4.34.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-2r53-9295-3m86
- https://nvd.nist.gov/vuln/detail/CVE-2023-48217
- https://github.com/statamic/cms/pull/8991
- https://github.com/statamic/cms/pull/8992
- https://github.com/statamic/cms/commit/4c6fe041e2203a8033e5949ce4a5d9d6c0ad2411
- https://github.com/statamic/cms/commit/da28afde818d605179fbb63b96eabafabad876b6
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v3.4.14
- https://github.com/statamic/cms/releases/tag/v4.34.0
