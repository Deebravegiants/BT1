# [H] compression vulnerable to Denial of Service via memory leak on premature response close

## Summary
Severity: High
Advisory: CVE-2026-87776
Aliases: GHSA-vc2v-76pw-4v95
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-87776
Type: osv

## Details
compression is a Node.js and Express compression middleware. In versions before 1.8.2, when a client aborts the connection while a compressed response is still being sent, the zlib stream created to compress that response is never destroyed, so each aborted compressed response leaks its native zlib memory. A remote unauthenticated attacker can repeatedly open requests and disconnect early, exhausting the available memory and crashing the server. All applications using compression are affected. The issue is fixed in compression 1.8.2, and users should upgrade to 1.8.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87776.json
- https://github.com/expressjs/compression/security/advisories/GHSA-vc2v-76pw-4v95
- https://nvd.nist.gov/vuln/detail/CVE-2026-87776
