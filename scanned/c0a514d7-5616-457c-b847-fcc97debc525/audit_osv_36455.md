# [M] Collabora Online vulnerable to Authorization Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-23623
Aliases: GHSA-68v6-r6qq-mmq2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-05
Source: https://osv.dev/vulnerability/CVE-2026-23623
Type: osv

## Details
Collabora Online is a collaborative online office suite based on LibreOffice technology. Prior to Collabora Online Development Edition version 25.04.08.2 and prior to Collabora Online versions 23.05.20.1, 24.04.17.3, and 25.04.7.5, a user with view-only rights and no download privileges can obtain a local copy of a shared file. Although there are no corresponding buttons in the interface, pressing Ctrl+Shift+S initiates the file download process. This allows the user to bypass the access restrictions and leads to unauthorized data retrieval. This issue has been patched in Collabora Online Development Edition version 25.04.08.2 and Collabora Online versions 23.05.20.1, 24.04.17.3, and 25.04.7.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23623.json
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-68v6-r6qq-mmq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-23623
