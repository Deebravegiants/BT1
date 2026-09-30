# [H] OpenEMR Portal Users Can Forge Provider Signatures

## Summary
Severity: High
Advisory: CVE-2026-24890
Aliases: GHSA-xc8x-mfh8-9xvh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-24890
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, an authorization bypass vulnerability in the patient portal signature endpoint allows authenticated portal users to upload and overwrite provider signatures by setting `type=admin-signature` and specifying any provider user ID. This could potentially lead to signature forgery on medical documents, legal compliance violations, and fraud. The issue occurs when portal users are allowed to modify provider signatures without proper authorization checks. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24890.json
- https://github.com/openemr/openemr/security/advisories/GHSA-xc8x-mfh8-9xvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24890
- https://github.com/openemr/openemr/commit/a29c0f7ac0975429a85cd09a3ff12ee0dcdb4478
