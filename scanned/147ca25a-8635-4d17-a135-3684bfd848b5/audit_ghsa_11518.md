# [H] Statamic has Stored XSS via SVG Sanitization Bypass

## Summary
Severity: High
Advisory: GHSA-7rcv-55mj-chg7
CVE: CVE-2026-33172
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-7rcv-55mj-chg7
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.0
- Packagist: `statamic/cms` — affected >=0 <5.73.14

## Details
### Impact

Stored XSS vulnerability in SVG asset reuploads allows authenticated users with asset upload permissions to bypass SVG sanitization and inject malicious JavaScript that executes when the asset is viewed.

### Patches

This has been fixed in 5.73.14 and 6.7.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-7rcv-55mj-chg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33172
- https://github.com/statamic/cms
