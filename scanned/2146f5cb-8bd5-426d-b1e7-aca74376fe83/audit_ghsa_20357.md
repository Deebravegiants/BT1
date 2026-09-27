# [H] Improper quoting of columns when using setOrderBy() or setGroupBy() on listing classes in Pimcore

## Summary
Severity: High
Advisory: GHSA-gvmf-wcx6-p974
CVE: CVE-2022-31092
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-22
Source: https://github.com/advisories/GHSA-gvmf-wcx6-p974
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.4.4

## Details
### Impact
Pimcore offers developers listing classes to make querying data easier. This listing classes also allow to order or group the results based on one or more columns which should be quoted by default. 
The actual issue is that quoting is not done properly in both cases, so there's the theoretical possibility to inject custom SQL if the developer is using this methods with input data and not doing proper input validation in advance and  so relies on the auto-quoting being done by the listing classes. 

##### Example: 
```php
// request url: https://example.com/foo?groupBy=o_id`; SELECT SLEEP(20);--

$list = new DataObject\Car\Listing();
$list->setOrderKey($request->get('orderBy'));
$list->setGroupBy($request->get('groupBy'));
$list->load();
```

### Patches
Upgrade to >= 10.4.4 or apply the following patch manually: 
https://github.com/pimcore/pimcore/commit/21559c6bf0e4e828d33ff7af6e88caecb5ac6549.patch

### Workarounds
Apply this patch manually: 
https://github.com/pimcore/pimcore/commit/21559c6bf0e4e828d33ff7af6e88caecb5ac6549.patch

### References
https://github.com/pimcore/pimcore/pull/12444

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-gvmf-wcx6-p974
- https://nvd.nist.gov/vuln/detail/CVE-2022-31092
- https://github.com/pimcore/pimcore/pull/12444
- https://github.com/pimcore/pimcore/commit/21559c6bf0e4e828d33ff7af6e88caecb5ac6549
- https://github.com/pimcore/pimcore
