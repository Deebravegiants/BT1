# [M] OpenEMR Patient Picture Context Allows Arbitrary Patient Photo Retrieval

## Summary
Severity: Medium
Advisory: CVE-2026-25929
Aliases: GHSA-778w-r8rm-8qhq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25929
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the document controller’s `patient_picture` context serves the patient’s photo by document ID or patient ID without verifying that the current user is authorized to access that patient. An authenticated user with document ACL can supply another patient’s ID and retrieve their photo. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25929.json
- https://github.com/openemr/openemr/security/advisories/GHSA-778w-r8rm-8qhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25929
- https://github.com/openemr/openemr/commit/fc4d00ecb63561dacd23cb1fed49c64bd1a83258
