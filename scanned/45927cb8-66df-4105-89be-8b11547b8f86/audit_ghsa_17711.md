# [M] ps_contactinfo has a potential XSS due to usage of the nofilter tag in template

## Summary
Severity: Medium
Advisory: GHSA-35pq-7pv2-2rfw
CVE: CVE-2025-24027
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-35pq-7pv2-2rfw
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_contactinfo` — affected >=0 <3.3.3

## Details
### Impact
This can not be exploited in a fresh install of PrestaShop, only shops made vulnerable by third party modules are concerned. 

For example, if your shop has a third party module vulnerable to SQL injections, then ps_contactinfo might execute a stored XSS in FO.

### Patches
The long term fix is to have all your modules maintained and updated.
The fix on ps_contactinfo will keep formatted addresses from displaying an xss stored in the database.

### Workarounds
none

### References
none

## References
- https://github.com/PrestaShop/ps_contactinfo/security/advisories/GHSA-35pq-7pv2-2rfw
- https://nvd.nist.gov/vuln/detail/CVE-2025-24027
- https://github.com/PrestaShop/ps_contactinfo/commit/d60f9a5634b4fc2d3a8831fb08fe2e1f23cbfa39
- https://github.com/PrestaShop/ps_contactinfo
