# [M] Flare: Private File IDOR via raw/direct endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-30231
Aliases: GHSA-gwqr-xf5c-5569
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-30231
Type: osv

## Details
Flare is a Next.js-based, self-hostable file sharing platform that integrates with screenshot tools. Prior to version 1.7.2, the raw and direct file routes only block unauthenticated users from accessing private files. Any authenticated, non‑owner user who knows the file URL can retrieve the content, which is inconsistent with stricter checks used by other endpoints. This issue has been patched in version 1.7.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30231.json
- https://github.com/FlintSH/Flare/security/advisories/GHSA-gwqr-xf5c-5569
- https://nvd.nist.gov/vuln/detail/CVE-2026-30231
