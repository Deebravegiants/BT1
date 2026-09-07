# [H] Inline attribute values were not processed.

## Summary
Severity: High
Advisory: GHSA-589w-hccm-265x
CVE: CVE-2020-15263
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-10-19
Source: https://github.com/advisories/GHSA-589w-hccm-265x
Type: github-advisory

## Affected
- Packagist: `orchid/platform` — affected >=9.0.0 <9.4.4

## Details
### Impact
Inline attributes have not been processed escape.
If the data that came from users was not processed, then an XSS vulnerability is possible

### Patches
Fixed in 9.4.4

## References
- https://github.com/orchidsoftware/platform/security/advisories/GHSA-589w-hccm-265x
- https://nvd.nist.gov/vuln/detail/CVE-2020-15263
- https://github.com/orchidsoftware/platform/commit/03f9a113b1a70bc5075ce86a918707f0e7d82169
