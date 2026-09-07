# [M] Pimcore Ecommerce Framework Bundle Improper Access Control allows unprivileged user to access back-office orders list

## Summary
Severity: Medium
Advisory: GHSA-cx99-25hr-5jxf
CVE: CVE-2024-21665
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-cx99-25hr-5jxf
Type: github-advisory

## Affected
- Packagist: `pimcore/ecommerce-framework-bundle` — affected >=0 <1.0.10

## Details
### Summary
An authenticated and unauthorized user can access the back-office orders list and be able to query over the information returned.

### Details
Permissions do not seem to be enforced when reaching the `admin/ecommerceframework/admin-order/list` endpoint allowing an authenticated user without the permissions to access the endpoint and query the data available there. It seems that the access control is not enforced in this place :

<https://github.com/pimcore/ecommerce-framework-bundle/blob/ff6ff287b6eb468bb940909c56970363596e5c21/src/Controller/AdminOrderController.php#L98>

__Note__ :  Testing this vulnerability requires a fully configured ecommerce website, but it looks vulnerable as when requesting the endpoint the data seem returned (and when looking at the source code nothing seems to validate the permissions on the specified endpoint).

### PoC
In order to reproduce the issue, the following steps can be followed :

1.  As an administrator :
  a. Create a role without any permission through Settings → User & Roles → Roles in the administration panel
  b. Create an user through Settings → User & Roles → Users and assign it the unprivileged role previously created
2. Log out the current administrator and log in with this new user
3. Access to the following endpoint `https://pimcore_instance/admin/ecommerceframework/admin-order/list` and the results will be returned to this unauthorized user

### Impact
An unauthorized user can access back-office orders without being authorized to.

## References
- https://github.com/pimcore/ecommerce-framework-bundle/security/advisories/GHSA-cx99-25hr-5jxf
- https://nvd.nist.gov/vuln/detail/CVE-2024-21665
- https://github.com/pimcore/ecommerce-framework-bundle/commit/05dec000ed009828084d05cf686f468afd1f464e
- https://github.com/pimcore/ecommerce-framework-bundle
- https://github.com/pimcore/ecommerce-framework-bundle/blob/ff6ff287b6eb468bb940909c56970363596e5c21/src/Controller/AdminOrderController.php#L98
- https://github.com/pimcore/ecommerce-framework-bundle/releases/tag/v1.0.10
