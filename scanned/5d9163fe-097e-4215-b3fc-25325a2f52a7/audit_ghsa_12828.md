# [M] Shopware vulnerable to Improper Input Validation of Clearance sale in cart

## Summary
Severity: Medium
Advisory: GHSA-8r6h-m72v-38fg
CVE: CVE-2023-22730
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-01-17
Source: https://github.com/advisories/GHSA-8r6h-m72v-38fg
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.18.1
- Packagist: `shopware/core` — affected >=0 <6.4.18.1

## Details
### Impact
It is possible to put the same line item multiple one in the cart using API, the Cart Validators checked the line item's individuality and the user was able to skip the clearance sale in cart

### Patches
The problem has been fixed with 6.4.18.1

### Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version. Or disable the newsletter registration completely.

### References
https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-01-2023?category=security-updates

## References
- https://github.com/shopware/platform/security/advisories/GHSA-8r6h-m72v-38fg
- https://nvd.nist.gov/vuln/detail/CVE-2023-22730
- https://github.com/shopware/platform/commit/4fce12096e54b2033832d9104fa2e68888c2b4e9
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-01-2023?category=security-updates
- https://github.com/shopware/platform
