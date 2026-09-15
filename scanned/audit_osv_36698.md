# [H] OpenEMR has Broken Access Control in Procedures Configuration

## Summary
Severity: High
Advisory: CVE-2026-25131
Aliases: GHSA-6h2m-4ppf-ph4j
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25131
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, a Broken Access Control vulnerability exists in the OpenEMR order types management system, allowing low-privilege users (such as Receptionist) to add and modify procedure types without proper authorization. This vulnerability is present in the /openemr/interface/orders/types_edit.php endpoint. Version 8.0.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25131.json
- https://github.com/openemr/openemr/security/advisories/GHSA-6h2m-4ppf-ph4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-25131
- https://github.com/openemr/openemr/commit/1e63cbab34558bca029533f87cdb6efb1ff32c75
