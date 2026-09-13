# [M] OpenEMR's Eye Exam View Trusts form_id Without Verifying Patient/Encounter Ownership

## Summary
Severity: Medium
Advisory: CVE-2026-27943
Aliases: GHSA-q96x-qw99-6xq9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27943
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. In versions up to and including 8.0.0, the eye exam (eye_mag) view loads data by `form_id` (or equivalent) without verifying that the form belongs to the current user’s patient/encounter context. An authenticated user can access or edit any patient’s eye exam by supplying another form ID; in some flows the session’s active patient may also be switched. A fix is available on the `main` branch of the OpenEMR GitHub repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27943.json
- https://github.com/openemr/openemr/security/advisories/GHSA-q96x-qw99-6xq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27943
- https://github.com/openemr/openemr/commit/c87489bf63f2701b634d948279e104f2ed3df1c0
