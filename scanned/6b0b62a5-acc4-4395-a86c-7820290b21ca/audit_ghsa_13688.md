# [M] PrestaShop blockreassurance BO User can remove any file from server when adding a and deleting a block

## Summary
Severity: Medium
Advisory: GHSA-83j2-qhx2-p7jc
CVE: CVE-2023-47109
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2023-11-08
Source: https://github.com/advisories/GHSA-83j2-qhx2-p7jc
Type: github-advisory

## Affected
- Packagist: `prestashop/blockreassurance` — affected >=0 <5.1.4

## Details
### Impact
When adding a block in blockreassurance module, a BO user can modify the http request and give the path of any file in the project instead of an image. When deleting the block from the BO, the file will be deleted.

It is possible to make the website completely unavailable by removing index.php for example.

### Patches
v5.1.4

### Workarounds
No workaround available

### References

## References
- https://github.com/PrestaShop/blockreassurance/security/advisories/GHSA-83j2-qhx2-p7jc
- https://nvd.nist.gov/vuln/detail/CVE-2023-47109
- https://github.com/PrestaShop/blockreassurance/commit/2d0e97bebf795690caffe33c1ab23a9bf43fcdfa
- https://github.com/PrestaShop/blockreassurance/commit/eec00da564db4c1804b0a0d1e3d9f7ec4e27d823
- https://github.com/PrestaShop/blockreassurance
- https://github.com/PrestaShop/blockreassurance/releases/tag/v5.1.4
