# [C] Blind SQL injection in shopware

## Summary
Severity: Critical
Advisory: GHSA-qmp9-2xwj-m6m9
CVE: CVE-2024-22406
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2024-01-17
Source: https://github.com/advisories/GHSA-qmp9-2xwj-m6m9
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.5.7.4
- Packagist: `shopware/platform` — affected >=0 <6.5.7.4

## Details
### Impact
The Shopware application API contains a search functionality which enables users to search through information stored within their Shopware instance. The searches performed by this function can be aggregated using the parameters in the “aggregations”
object. The ‘name’ field in this “aggregations” object is vulnerable SQL-injection and can be exploited using time-based SQL-queries. 

### Patches
Update to Shopware 6.5.7.4

### Workarounds
For older versions of 6.1, 6.2, 6.3 and 6.4 corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-qmp9-2xwj-m6m9
- https://nvd.nist.gov/vuln/detail/CVE-2024-22406
- https://github.com/shopware/core/commit/e2256ec81e56f792623e90d89786d8a9fcad28bf
- https://github.com/shopware/shopware/commit/5005213e609f5a4423fcfa92f105c3de8ab35100
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.5.7.4
