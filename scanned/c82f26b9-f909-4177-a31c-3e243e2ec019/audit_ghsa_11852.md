# [M] Statamic's live preview token bypasses content protection for unrelated entries

## Summary
Severity: Medium
Advisory: GHSA-8vwx-ccf6-5wg2
CVE: CVE-2026-33884
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-8vwx-ccf6-5wg2
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.2

## Details
### Impact
An authenticated Control Panel user with access to live preview could use a live preview token to access restricted content that the token was not intended for.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-8vwx-ccf6-5wg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33884
- https://github.com/statamic/cms
