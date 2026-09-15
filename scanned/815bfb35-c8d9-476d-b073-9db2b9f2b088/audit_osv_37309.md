# [M] Flare has a Path Traversal in /api/avatars/[filename]

## Summary
Severity: Medium
Advisory: CVE-2026-30942
Aliases: GHSA-h639-p7m9-mpgp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30942
Type: osv

## Details
Flare is a Next.js-based, self-hostable file sharing platform that integrates with screenshot tools. Prior to 1.7.3, an authenticated path traversal vulnerability in /api/avatars/[filename] allows any logged-in user to read arbitrary files from within the application container. The filename URL parameter is passed to path.join() without sanitization, and getFileStream() performs no path validation, enabling %2F-encoded ../ sequences to escape the uploads/avatars/ directory and read any file accessible to the nextjs process under /app/. Authentication is enforced by Next.js middleware. However, on instances with open registration enabled (the default), any attacker can self-register and immediately exploit this. This vulnerability is fixed in 1.7.3.

## References
- https://github.com/FlintSH/Flare/releases/tag/v1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30942.json
- https://github.com/FlintSH/Flare/security/advisories/GHSA-h639-p7m9-mpgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30942
- https://github.com/FlintSH/Flare/commit/cd894cc480619aef958be5de72b1445222fd8d36
