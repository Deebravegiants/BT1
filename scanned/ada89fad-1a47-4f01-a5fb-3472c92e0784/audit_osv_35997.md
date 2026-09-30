# [H] Velociraptor directory traversal via the NewNotebook API

## Summary
Severity: High
Advisory: CVE-2026-18640
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18640
Type: osv

## Details
The NewNotebook API does not sufficiently sanitize its parameters allowing an authenticated user with NOTEBOOK_EDIT permission to write the notebook record outside the org's data store directory. The file written must have an extension of ".json.db" but can otherwise overwrite other metadata files (such as ACL records, hunts etc). This can corrupt these files and cause data corruption.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18640/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18640.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18640
