# [M] Shopware 6 allows attackers to check for registered accounts through the store-api

## Summary
Severity: Medium
Advisory: GHSA-hh7j-6x3q-f52h
CVE: CVE-2025-30150
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-hh7j-6x3q-f52h
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.6.0.0 <6.6.10.3
- Packagist: `shopware/platform` — affected >=6.6.0.0 <6.6.10.3
- Packagist: `shopware/core` — affected >=6.7.0.0-rc1 <6.7.0.0-rc2
- Packagist: `shopware/platform` — affected >=6.7.0.0-rc1 <6.7.0.0-rc2
- Packagist: `shopware/core` — affected >=0 <6.5.8.18
- Packagist: `shopware/platform` — affected >=0 <6.5.8.18

## Details
### Impact
Through the store-api it is possible as a attacker to check if a specific e-mail address has an account in the shop.

Using the store-api endpoint `/store-api/account/recovery-password` you get the response
```
{"errors":[{"status":"404","code":"CHECKOUT__CUSTOMER_NOT_FOUND","title":"Not Found","detail":"No matching customer for the email \u0022asdasfd@asdads.de\u0022 was found.","meta":{"parameters":{"email":"asdasfd@asdads.de"}}}]}
```

which indicates clearly that there is no account for this customer. In contrast you get a success response if the account was found.

### Patches
Update to Shopware 6.6.10.3

### Workarounds
For older versions of 6.5 or 6.4, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-hh7j-6x3q-f52h
- https://nvd.nist.gov/vuln/detail/CVE-2025-30150
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.5.8.17
- https://github.com/shopware/shopware/releases/tag/v6.6.10.3
- https://github.com/shopware/shopware/releases/tag/v6.7.0.0-rc2
