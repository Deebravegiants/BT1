# [M] CVE-2020-15085

## Summary
Severity: Medium
Advisory: CVE-2020-15085
Aliases: GHSA-4279-h39w-2jqm
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-15085
Type: osv

## Details
In Saleor Storefront before version 2.10.3, request data used to authenticate customers was inadvertently cached in the browser's local storage mechanism, including credentials. A malicious user with direct access to the browser could extract the email and password. In versions prior to 2.10.0 persisted the cache even after the user logged out. This is fixed in version 2.10.3. A workaround is to manually clear application data (browser's local storage) after logging into Saleor Storefront.

## References
- https://github.com/mirumee/saleor-storefront/blob/master/CHANGELOG.md#2103
- https://github.com/mirumee/saleor-storefront/security/advisories/GHSA-4279-h39w-2jqm
- https://github.com/mirumee/saleor-storefront/commit/7c331e1be805022c9a7be719bd69d050b2577458
