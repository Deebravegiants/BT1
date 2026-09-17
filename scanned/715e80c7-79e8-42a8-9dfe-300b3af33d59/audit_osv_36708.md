# [H] OpenEMR's Document and Insurance REST Endpoints Skip ACL

## Summary
Severity: High
Advisory: CVE-2026-25164
Aliases: GHSA-f64c-h2gh-g3f9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25164
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the REST API route table in `apis/routes/_rest_routes_standard.inc.php` does not call `RestConfig::request_authorization_check()` for the document and insurance routes. Other patient routes in the same file (e.g. encounters, patients/med) call it with the appropriate ACL. As a result, any valid API bearer token can access or modify every patient's documents and insurance data, regardless of the token’s OpenEMR ACLs—effectively exposing all document and insurance PHI to any authenticated API client. Version 8.0.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25164.json
- https://github.com/openemr/openemr/security/advisories/GHSA-f64c-h2gh-g3f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25164
- https://github.com/openemr/openemr/commit/c5e1c44774156cd0d04f4e08ed6a81fe76d38e92
