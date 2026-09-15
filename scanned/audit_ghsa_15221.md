# [M] Pimcore Customer Data Framework Improper Access Control allows unprivileged user to access customers duplicates list

## Summary
Severity: Medium
Advisory: GHSA-c38c-c8mh-vq68
CVE: CVE-2024-21666
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-c38c-c8mh-vq68
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <4.0.6

## Details
### Summary
An authenticated and unauthorized user can access the list of potential duplicate users and see their data.

### Details
Permissions do not seem to be enforced when reaching the `/admin/customermanagementframework/duplicates/list` endpoint allowing an authenticated user without the permissions to access the endpoint and query the data available there. It seems that the access control is not enforced in this place :
<https://github.com/pimcore/customer-data-framework/blob/b4af625ef327c58d05ef7cdf145fa749d2d4195e/src/Controller/Admin/DuplicatesController.php#L43>

### PoC
In order to reproduce the issue, the following steps can be followed :

1. As an administrator :
  a. Create a role without any permission through Settings → User & Roles → Roles in the administration panel
  b. Create an user through Settings → User & Roles → Users and assign it the unprivileged role previously created
2. Log out the current administrator and log in with this new user
3. Access to the following endpoint `https://pimcore_instance/admin/customermanagementframework/duplicates/list` and the results will be returned to this unauthorized user

### Impact
An unauthorized user can access PII data from customers without being authorized to.

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-c38c-c8mh-vq68
- https://nvd.nist.gov/vuln/detail/CVE-2024-21666
- https://github.com/pimcore/customer-data-framework/commit/c33c0048390ef0cf98b801d46a81d0762243baa6
- https://github.com/pimcore/customer-data-framework
- https://github.com/pimcore/customer-data-framework/blob/b4af625ef327c58d05ef7cdf145fa749d2d4195e/src/Controller/Admin/DuplicatesController.php#L43
