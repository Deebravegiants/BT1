# [M] Pimcore missing token/header to prevent CSRF

## Summary
Severity: Medium
Advisory: CVE-2023-49076
Aliases: GHSA-xx63-4jr8-9ghc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2023-11-30
Source: https://osv.dev/vulnerability/CVE-2023-49076
Type: osv

## Details
Customer-data-framework allows management of customer data within Pimcore. There are no tokens or headers to prevent CSRF attacks from occurring, therefore an attacker could abuse this vulnerability to create new customers. This issue has been patched in version 4.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49076.json
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-xx63-4jr8-9ghc
- https://nvd.nist.gov/vuln/detail/CVE-2023-49076
- https://github.com/pimcore/customer-data-framework/commit/ef7414415cfa64189b8433eff0aa2a9b537a89f7.patch
