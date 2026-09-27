# [M] Strapi's field level permissions not being respected in relationship title

## Summary
Severity: Medium
Advisory: GHSA-m284-85mf-cgrc
CVE: CVE-2023-37263
CWE: CWE-200, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-m284-85mf-cgrc
Type: github-advisory

## Affected
- npm: `@strapi/plugin-content-manager` — affected >=0 <4.12.1

## Details
### Summary
Field level permissions not being respected in relationship title.
If I have a  relationship title and the relationship shows a field I don't have permission to see I will still be visible.

### Details
No RBAC checks on on the relationship the relation endpoint returns

### PoC
#### Setup
Create a fresh strapi instance
Create a new content type
in the newly created content type add a relation to the users-permissions user.
Save.
Create a users-permissions user
Use your created  content type and create an entry in it related to the users-permisisons user

Go to settings -> Admin panel -> Roles -> Author
Give the author role full permissions on the content type your created.
Make sure they don't have any permission to see User
Save

Create a new admin account with only the author role
#### CVE
login on the newly created author acount.
go to the content manager to the colection type you created with the relationship to users_permissions_user
You now see a field you don't have permissions to view.

### Impact
RBAC field level checks leaks data selected by the admin user as relationship title
What could be sensitive fields that they should not be allowed to see. by the person having this specific role.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-m284-85mf-cgrc
- https://nvd.nist.gov/vuln/detail/CVE-2023-37263
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.12.1
