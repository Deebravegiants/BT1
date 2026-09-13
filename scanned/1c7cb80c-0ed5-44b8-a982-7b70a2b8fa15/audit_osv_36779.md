# [M] OpenEMR: POST /api/.../vital Accepts Attacker-Supplied id and Overwrites Arbitrary Vitals

## Summary
Severity: Medium
Advisory: CVE-2026-25744
Aliases: GHSA-mv9m-j65p-g55f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-25744
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.2, the encounter vitals API accepts an `id` in the request body and treats it as an UPDATE. There is no verification that the vital belongs to the current patient or encounter. An authenticated user with encounters/notes permission can overwrite any patient's vitals by supplying another patient's vital `id`, leading to medical record tampering. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25744.json
- https://github.com/openemr/openemr/security/advisories/GHSA-mv9m-j65p-g55f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25744
- https://github.com/openemr/openemr/commit/c3a47c37619cdb4f0aaa168e39a93ab1d106429c
