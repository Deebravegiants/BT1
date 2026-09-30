# [M] Pimcore Admin Classic Bundle permissions are not getting checked when working with tags

## Summary
Severity: Medium
Advisory: GHSA-3rfr-mpfj-2jwq
CVE: CVE-2024-24822
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-3rfr-mpfj-2jwq
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.3.3

## Details
### Impact
You can create, delete etc. tags without having the permission to do so.
This vulnerability allows an attacker to perform broken access control and add tags to admin panel and add dumy data. One can do this as intruder and add text parameters with random numbers and this will effect integrity and availability.

### Patches
Available in version 1.3.3.

### Workarounds
Apply this pull request manually: https://github.com/pimcore/admin-ui-classic-bundle/pull/412

### References
-

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-3rfr-mpfj-2jwq
- https://nvd.nist.gov/vuln/detail/CVE-2024-24822
- https://github.com/pimcore/admin-ui-classic-bundle/pull/412
- https://github.com/pimcore/admin-ui-classic-bundle/commit/24660b6d5ad9cbcb037a48d4309a6024e9adf251
- https://github.com/pimcore/admin-ui-classic-bundle
