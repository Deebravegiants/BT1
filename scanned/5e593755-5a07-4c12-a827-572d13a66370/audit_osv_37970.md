# [H] OpenEMR has a Privilege Escalation that Allows a Low-Level User to View Admin-Only Data

## Summary
Severity: High
Advisory: CVE-2026-34056
Aliases: GHSA-6qg7-6jf3-xrfh
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-34056
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. A Broken Access Control vulnerability in OpenEMR up to and including version 8.0.0.3 allows low-privilege users to view and download Ensora eRx error logs without proper authorization checks. This flaw compromises system confidentiality by exposing sensitive information, potentially leading to unauthorized data disclosure and misuse. As of time of publication, no known patches versions are available.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34056.json
- https://github.com/openemr/openemr/security/advisories/GHSA-6qg7-6jf3-xrfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34056
