# [H] OpenEMR: Inverted ACL Condition in CDR ControllerRouter Allows Any Authenticated User to Modify/Delete Clinical Rules and Plans

## Summary
Severity: High
Advisory: CVE-2026-32126
Aliases: GHSA-752v-x6m4-6cf8
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32126
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.1, an inverted boolean condition in ControllerRouter::route() causes the admin/super ACL check to be enforced only for controllers that already have their own internal authorization (review, log), while leaving all other CDR controllers — alerts, ajax, edit, add, detail, browse — accessible to any authenticated user. This allows any logged-in user to suppress clinical decision support alerts system-wide, delete or modify clinical plans, and edit rule configurations — all operations intended to require administrator privileges. This vulnerability is fixed in 8.0.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32126.json
- https://github.com/openemr/openemr/security/advisories/GHSA-752v-x6m4-6cf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32126
