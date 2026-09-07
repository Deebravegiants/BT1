# [H] Improper Removal of Sensitive Information Before Storage or Transfer in Strapi

## Summary
Severity: High
Advisory: GHSA-f6fm-r26q-p747
CVE: CVE-2022-30617
CWE: CWE-212
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-20
Source: https://github.com/advisories/GHSA-f6fm-r26q-p747
Type: github-advisory

## Affected
- npm: `strapi` — affected >=3.0.0 <3.6.9
- npm: `@strapi/strapi` — affected >=0 <4.0.0-beta.15

## Details
An authenticated user with access to the Strapi admin panel can view private and sensitive data, such as email and password reset tokens, for other admin panel users that have a relationship (e.g., created by, updated by) with content accessible to the authenticated user. For example, a low-privileged “author” role account can view these details in the JSON response for an “editor” or “super admin” that has updated one of the author’s blog posts. There are also many other scenarios where such details from other users can leak in the JSON response, either through a direct or indirect relationship. Access to this information enables a user to compromise other users’ accounts by successfully invoking the password reset workflow. In a worst-case scenario, a low-privileged user could get access to a “super admin” account with full control over the Strapi instance, and could read and modify any data as well as block access to both the admin panel and API by revoking privileges for all other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30617
- https://github.com/strapi/strapi
- https://www.synopsys.com/blogs/software-security/cyrc-advisory-strapi
