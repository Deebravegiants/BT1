# [M] OpenEMR has Authorization Bypass in Dated Reminders Log

## Summary
Severity: Medium
Advisory: CVE-2026-33304
Aliases: GHSA-66j9-ffq4-h222
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33304
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.2, an authorization bypass in the dated reminders log allows any authenticated non-admin user to view reminder messages belonging to other users, including associated patient names and free-text message content, by crafting a GET request with arbitrary user IDs in the `sentTo[]` or `sentBy[]` parameters. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33304.json
- https://github.com/openemr/openemr/security/advisories/GHSA-66j9-ffq4-h222
- https://nvd.nist.gov/vuln/detail/CVE-2026-33304
- https://github.com/openemr/openemr/commit/21dee7658a5f3b18c5750e3fae7324e875c1703a
