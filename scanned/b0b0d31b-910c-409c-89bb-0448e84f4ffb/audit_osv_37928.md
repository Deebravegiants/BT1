# [H] OpenEMR: XInclude Injection in CCDA Import Allows Reading Arbitrary Server Files

## Summary
Severity: High
Advisory: CVE-2026-33913
Aliases: GHSA-9757-3cfj-wc8q
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33913
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, an authenticated user with access to the Carecoordination module can upload a crafted CCDA document containing `<xi:include href="file:///etc/passwd" parse="text"/>` to read arbitrary files from the server. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33913.json
- https://github.com/openemr/openemr/security/advisories/GHSA-9757-3cfj-wc8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33913
- https://github.com/openemr/openemr/commit/67e1702c41cf486af0069bdafce19860e2cd9a11
