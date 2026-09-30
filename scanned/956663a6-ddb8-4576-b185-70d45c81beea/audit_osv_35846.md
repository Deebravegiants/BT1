# [M] morgan vulnerable to Log Forging via unescaped Unicode line separators

## Summary
Severity: Medium
Advisory: CVE-2026-15603
Aliases: GHSA-jxfw-x594-9x9m
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-15603
Type: osv

## Details
morgan is an HTTP request logger middleware for Node.js. In versions prior to 1.12.0, the internal helper that escapes log token values did not neutralize the Unicode line separator characters U+0085 (Next Line), U+2028 (Line Separator), and U+2029 (Paragraph Separator). An unauthenticated remote client can place these characters in an attacker-controlled log token, for example a Basic auth username surfaced through the remote-user token, so that Unicode-aware downstream log processing splits a single request log into multiple logical records. This is a log forging issue (CWE-117) and an incomplete-fix follow-up to CVE-2026-5078, which only addressed ASCII control characters. The issue is fixed in morgan 1.12.0, which extends the escaping set to cover these Unicode line separators. Upgrade to morgan 1.12.0 to remediate.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15603.json
- https://github.com/expressjs/morgan/security/advisories/GHSA-jxfw-x594-9x9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-15603
