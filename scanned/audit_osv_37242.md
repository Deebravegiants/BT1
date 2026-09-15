# [M] OpenProject BIM BCF XML Import: <Snapshot> Path Traversal Leads to Arbitrary Local File Read (AFR)

## Summary
Severity: Medium
Advisory: CVE-2026-30234
Aliases: GHSA-q8c5-vpmm-xrxv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-30234
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.2.0, an authenticated project member with BCF import permissions can upload a crafted .bcf archive where the <Snapshot> value in markup.bcf is manipulated to contain an absolute or traversal local path (for example: /etc/passwd or ../../../../etc/passwd). During import, this untrusted <Snapshot> value is used as file.path during attachment processing. As a result, local filesystem content can be read outside the intended ZIP scope. This results in an Arbitrary File Read (AFR) within the read permissions of the OpenProject application user. This vulnerability is fixed in 17.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30234.json
- https://github.com/opf/openproject/security/advisories/GHSA-q8c5-vpmm-xrxv
- https://nvd.nist.gov/vuln/detail/CVE-2026-30234
