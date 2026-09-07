# [M] Snipe-IT has Stored XSS via Component Checkout Notes (v8.4.0)

## Summary
Severity: Medium
Advisory: GHSA-r42m-953q-6vjx
CVE: CVE-2026-44831
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-r42m-953q-6vjx
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.4.1

## Details
### Impact
Users with component view access could be impacted by an unescaped `notes` column. 

### Patches
This was patched in https://github.com/grokability/snipe-it/commit/28f493d84d057895fbb93b6570e7393a2c2fa438, and is fixed in v8.4.1 or greater. 

### Workarounds
None.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-r42m-953q-6vjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44831
- https://github.com/grokability/snipe-it/commit/28f493d84d057895fbb93b6570e7393a2c2fa438
- https://github.com/grokability/snipe-it
