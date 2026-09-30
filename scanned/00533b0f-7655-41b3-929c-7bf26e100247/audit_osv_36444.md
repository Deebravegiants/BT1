# [M] Traccar vulnerable to Path Traversal and External Control of File Name or Path

## Summary
Severity: Medium
Advisory: CVE-2026-23521
Aliases: GHSA-rc28-cvfc-chqr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2026-23521
Type: osv

## Details
Versions of the Traccar open-source GPS tracking system up to and including 6.11.1 contain an issue in which authenticated users who can create or edit devices can set a device `uniqueId` to an absolute path. When uploading a device image, Traccar uses that `uniqueId` to build the filesystem path without enforcing that the resolved path stays under the media root. This allows writing files outside the media directory. As of time of publication, it is unclear whether a fix is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23521.json
- https://github.com/traccar/traccar/security/advisories/GHSA-rc28-cvfc-chqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23521
