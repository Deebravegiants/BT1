# [M] Flare: Password‑Protected Thumbnail Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-30230
Aliases: GHSA-3x7v-x3r6-mjh7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-30230
Type: osv

## Details
Flare is a Next.js-based, self-hostable file sharing platform that integrates with screenshot tools. Prior to version 1.7.2, the thumbnail endpoint does not validate the password for password‑protected files. It checks ownership/admin for private files but skips password verification, allowing thumbnail access without the password. This issue has been patched in version 1.7.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30230.json
- https://github.com/FlintSH/Flare/security/advisories/GHSA-3x7v-x3r6-mjh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-30230
