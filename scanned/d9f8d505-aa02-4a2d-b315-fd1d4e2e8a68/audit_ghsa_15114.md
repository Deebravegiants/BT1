# [M] No permission checks for editing/deleting records with CSV import form

## Summary
Severity: Medium
Advisory: GHSA-j3m6-gvm8-mhvw
CVE: CVE-2023-49783
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-j3m6-gvm8-mhvw
Type: github-advisory

## Affected
- Packagist: `silverstripe/admin` — affected >=1.0.0 <1.13.19
- Packagist: `silverstripe/admin` — affected >=2.0.0 <2.1.8

## Details
### Impact
Users who don't have edit or delete permissions for records exposed in a `ModelAdmin` can still edit or delete records using the CSV import form, provided they have create permissions.

The likelyhood of a user having create permissions but _not_ having edit or delete permissions is low, but it _is_ possible.

Note that this doesn't affect any `ModelAdmin` which has had the import form disabled via the [`showImportForm` public property](https://api.silverstripe.org/4/SilverStripe/Admin/ModelAdmin.html#property_showImportForm), nor does it impact the `SecurityAdmin` section.

#### Action may be required

If you have a custom implementation of [`BulkLoader`](https://api.silverstripe.org/4/SilverStripe/Dev/BulkLoader.html), you should update your implementation to respect permissions when the return value of [`getCheckPermissions()`](https://api.silverstripe.org/4/SilverStripe/Dev/BulkLoader.html#method_getCheckPermissions) is true.

If you are using any `BulkLoader` in your own project logic, or maintain a module which uses it, you should consider passing `true` to [`setCheckPermissions()`](https://api.silverstripe.org/4/SilverStripe/Dev/BulkLoader.html#method_setCheckPermissions) if the data is provided by users.

**Base CVSS:** [4.3](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N/E:F/RL:O/RC:C&version=3.1)
**Reported by:** Guy Sartorelli from Silverstripe

### References
- https://www.silverstripe.org/download/security-releases/CVE-2023-49783

## References
- https://github.com/silverstripe/silverstripe-admin/security/advisories/GHSA-j3m6-gvm8-mhvw
- https://nvd.nist.gov/vuln/detail/CVE-2023-49783
- https://github.com/silverstripe-security/security-issues/issues/177
- https://github.com/silverstripeltd/product-issues/issues/832
- https://github.com/silverstripe/silverstripe-admin/commit/9693130a0a637cdf512277cf5f07e83250b191db
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/admin/CVE-2023-49783.yaml
- https://github.com/silverstripe/silverstripe-admin
- https://www.silverstripe.org/download/security-releases/CVE-2023-49783
