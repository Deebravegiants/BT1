# [C] Wiki.js: Privilege Escalation via Missing Group Validation in users.update

## Summary
Severity: Critical
Advisory: CVE-2026-44224
Aliases: GHSA-cq3g-mwrg-v2rv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44224
Type: osv

## Details
Wiki.js is an open source wiki app built on Node.js. Prior to 2.5.313, the users.update GraphQL mutation accepts an arbitrary groups array and applies it directly to the database with no validation of the group IDs supplied. The resolver passes the caller's arguments straight to the model without any ownership check or restriction on which groups can be assigned. A user with manage:users — a permission typically delegated to wiki moderators for account management — can set groups:[1] on their own account to self-assign to the Administrators group. After re-authentication, the fresh JWT carries manage:system, granting full site administrator access in a single mutation call. This vulnerability is fixed in 2.5.313.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44224.json
- https://github.com/requarks/wiki/security/advisories/GHSA-cq3g-mwrg-v2rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44224
