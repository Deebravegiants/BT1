# [M] Rapid7 Velociraptor Directory Traversal Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-14728
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-14728
Type: osv

## Details
Rapid7 Velociraptor versions before 0.75.6 contain a directory traversal issue on Linux servers that allows a rogue client to upload a file which is written outside the datastore directory. Velociraptor is normally only allowed to write in the datastore directory. The issue occurs due to insufficient sanitization of directory names which end with a ".", only encoding the final "." AS "%2E".


Although files can be written to incorrect locations, the containing directory must end with "%2E". This limits the impact of this vulnerability, and prevents it from overwriting critical files.

## References
- https://docs.velociraptor.app/announcements/advisories/cve-2025-14728/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14728.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14728
- https://github.com/Velocidex/velociraptor
