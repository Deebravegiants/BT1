# [M] OpenEMR has IDOR in Fee Sheet Product Save

## Summary
Severity: Medium
Advisory: CVE-2026-32120
Aliases: GHSA-pvvj-mv7h-7847
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-32120
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, an Insecure Direct Object Reference (IDOR) vulnerability in the fee sheet product save logic (`library/FeeSheet.class.php`) allows any authenticated user with fee sheet ACL access to delete, modify, or read `drug_sales` records belonging to arbitrary patients by manipulating the hidden `prod[][sale_id]` form field. The `save()` method uses the user-supplied `sale_id` in five SQL queries (SELECT, UPDATE, DELETE) without verifying that the record belongs to the current patient and encounter. Version 8.0.0.3 contains a patch.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32120.json
- https://github.com/openemr/openemr/security/advisories/GHSA-pvvj-mv7h-7847
- https://nvd.nist.gov/vuln/detail/CVE-2026-32120
- https://github.com/openemr/openemr/commit/c5b4dd8caf2af70617cc58d39188621ed90543dc
