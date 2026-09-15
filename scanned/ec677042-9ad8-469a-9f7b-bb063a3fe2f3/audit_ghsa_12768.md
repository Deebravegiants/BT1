# [M] Shopware has Improper Input Validation issue in newsletter subscription

## Summary
Severity: Medium
Advisory: GHSA-46h7-vj7x-fxg2
CVE: CVE-2023-22734
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-46h7-vj7x-fxg2
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.18.1
- Packagist: `shopware/core` — affected >=0 <6.4.18.1

## Details
### Impact

The newsletter double opt-in validation was not checked properly, and it was possible to skip the complete double opt in process.

### Patches
The problem has been fixed with 6.4.18.1

### Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version. Or disable the newsletter registration completely.

### References

https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-01-2023?category=security-updates

## References
- https://github.com/shopware/platform/security/advisories/GHSA-46h7-vj7x-fxg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-22734
- https://github.com/shopware/platform/commit/f5a95ee2bcf1e546878450963ef1d9886e59a620
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-01-2023?category=security-updates
- https://github.com/shopware/platform
