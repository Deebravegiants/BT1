# [H] efw4.X: readonly Flag Not Enforced Server-Side

## Summary
Severity: High
Advisory: CVE-2026-44260
Aliases: GHSA-5454-qhrf-vcvh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44260
Type: osv

## Details
efw4.X is an Enterprise Framework for Web. Prior to 4.08.010, the readonly flag set on the <efw:elFinder> JSP tag is intended to prevent file modifications. When protected=true, elfinder_checkRisk enforces that the client sends readonly=true (matching the session value), but no event handler checks the readonly value before performing write operations. The flag only controls client-side UI elements (disabling buttons) and response metadata (write: 0, locked: 1). An attacker who sends requests directly (bypassing the UI) can perform all file operations despite readonly=true. This vulnerability is fixed in 4.08.010.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44260.json
- https://github.com/efwGrp/efw4.X/security/advisories/GHSA-5454-qhrf-vcvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44260
