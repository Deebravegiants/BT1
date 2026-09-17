# [H] ChurchCRM: Improper object-level authorization allows low-privileged users to read and modify other families’ records

## Summary
Severity: High
Advisory: CVE-2026-58410
Aliases: GHSA-jjcj-h3cm-p7x7
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58410
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 7.4.0, there was an authorization flaw in the family-scoped endpoints which allowed low-privileged users to read and modify other families’ records. An authenticated non-admin user with EditSelf access can supply another family’s `familyId` and access records outside their own family scope. The backend trusts the attacker-controlled `familyId` and loads the corresponding family entity by ID without verifying that the requested family belongs to the current user. If the same user also has Notes permission, they can create notes on another family’s record. This breaks the intended EditSelf scope and allows access to unrelated congregation records. This issue has been fixed in version 7.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58410.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-jjcj-h3cm-p7x7
- https://nvd.nist.gov/vuln/detail/CVE-2026-58410
