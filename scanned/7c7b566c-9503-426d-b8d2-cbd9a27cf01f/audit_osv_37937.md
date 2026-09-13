# [M] OpenEMR's Missing Authorization in show-signature.php Allows Portal Patients to Read Staff Signatures

## Summary
Severity: Medium
Advisory: CVE-2026-33934
Aliases: GHSA-w9w5-7x6h-657q
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33934
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0.3 have a missing authorization check in `portal/sign/lib/show-signature.php` that allows any authenticated patient portal user to retrieve the drawn signature image of any staff member by supplying an arbitrary `user` value in the POST body. The companion write endpoint (`save-signature.php`) was already hardened against this same issue, but the read endpoint was not updated to match. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33934.json
- https://github.com/openemr/openemr/security/advisories/GHSA-w9w5-7x6h-657q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33934
- https://github.com/openemr/openemr/commit/ae7ee1872d2e6300b165e24687cc90cf6847a4e5
