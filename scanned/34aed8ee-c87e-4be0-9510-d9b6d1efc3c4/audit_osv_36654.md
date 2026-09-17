# [C] OpenEMR Arbitrary File Read Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-24849
Aliases: GHSA-w6vc-hx2x-48pc
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-24849
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 7.0.4, the `disposeDocument()` method in `EtherFaxActions.php` allows authenticated users to read arbitrary files from the server filesystem. Any authenticated user (regardless of privilege level) can exploit this vulnerability to read sensitive files. Version 7.0.4 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24849.json
- https://github.com/openemr/openemr/security/advisories/GHSA-w6vc-hx2x-48pc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24849
- https://github.com/openemr/openemr/commit/22f8e53e5769a88b7a16cb223bd197d044c84e5a
