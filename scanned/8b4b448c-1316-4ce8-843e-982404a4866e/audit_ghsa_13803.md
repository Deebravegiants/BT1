# [H] Cross-site Scripting via uploaded assets

## Summary
Severity: High
Advisory: GHSA-8jjh-j3c2-cjcv
CVE: CVE-2023-48701
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2023-11-22
Source: https://github.com/advisories/GHSA-8jjh-j3c2-cjcv
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <3.4.15
- Packagist: `statamic/cms` — affected >=4.0.0 <4.36.0

## Details
### Impact
HTML files crafted to look like images may be uploaded regardless of mime validation. This is only applicable on front-end forms using the "Forms" feature containing an assets field, or within the control panel which requires authentication.

### Patches
It has been patched on 3.4.15 and 4.36.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-8jjh-j3c2-cjcv
- https://nvd.nist.gov/vuln/detail/CVE-2023-48701
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v3.4.15
- https://github.com/statamic/cms/releases/tag/v4.36.0
