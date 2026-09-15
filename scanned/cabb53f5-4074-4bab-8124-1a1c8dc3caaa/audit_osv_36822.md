# [M] OpenEMR's Printable LBF Endpoint Leaks Arbitrary Patient Forms

## Summary
Severity: Medium
Advisory: CVE-2026-25930
Aliases: GHSA-h3xx-8cp7-hf7m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25930
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the Layout-Based Form (LBF) printable view accepts `formid` and `visitid` (or `patientid`) from the request and does not verify that the form belongs to the current user’s authorized patient/encounter. An authenticated user with LBF access can enumerate form IDs and view or print any patient’s encounter forms. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25930.json
- https://github.com/openemr/openemr/security/advisories/GHSA-h3xx-8cp7-hf7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-25930
- https://github.com/openemr/openemr/commit/8c76acdd226007cc4ff3eccd3ca6193e0be6e699
