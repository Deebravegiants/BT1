# [M] Pimcore Customer Data Framework Improper Access Control allows unprivileged user to access GDPR extracts

## Summary
Severity: Medium
Advisory: GHSA-g273-wppx-82w4
CVE: CVE-2024-21667
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-g273-wppx-82w4
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <4.0.6

## Details
### Summary
An authenticated and unauthorized user can access the GDPR data extraction feature and query over the information returned, leading to customer data exposure.

### Details
Permissions do not seem to be enforced when reaching the `/admin/customermanagementframework/gdpr-data/search-data-objects` endpoint allowing an authenticated user without the permissions to access the endpoint and query the data available there. It seems that the access control is not enforced in this place : <https://github.com/pimcore/customer-data-framework/blob/b4af625ef327c58d05ef7cdf145fa749d2d4195e/src/Controller/Admin/GDPRDataController.php#L38>

### PoC

In order to reproduce the issue, the following steps can be followed: 

1. As an administrator : 
  a. Create a role without any permission through Settings → User & Roles → Roles in the administration panel
  b. Create an user through Settings → User & Roles → Users and assign it the unprivileged role previously created
2. Log out the current administrator and log in with this new user
3. Access to the following endpoint `https://pimcore_instance/admin/customermanagementframework/gdpr-data/search-data-objects?id=&firstname=&lastname=&email=&page=1&start=0&limit=50` and the results will be returned to this unauthorized user.

### Impact
An unauthorized user can access PII data from customers without being authorized to.

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-g273-wppx-82w4
- https://nvd.nist.gov/vuln/detail/CVE-2024-21667
- https://github.com/pimcore/customer-data-framework/commit/6c34515be2ba39dceee7da07a1abf246309ccd77
- https://github.com/pimcore/customer-data-framework
- https://github.com/pimcore/customer-data-framework/blob/b4af625ef327c58d05ef7cdf145fa749d2d4195e/src/Controller/Admin/GDPRDataController.php#L38
