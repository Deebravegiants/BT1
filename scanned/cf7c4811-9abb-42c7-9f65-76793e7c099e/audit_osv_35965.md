# [M] @fastify/forwarded vulnerable to improper input validation via unstripped tab characters in X-Forwarded-For

## Summary
Severity: Medium
Advisory: CVE-2026-18174
Aliases: GHSA-2849-m2w7-xm8f
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-18174
Type: osv

## Details
@fastify/forwarded resolves client addresses from the X-Forwarded-For header. In versions before 3.0.2, when the header contains two or more comma separated entries, the parser trims only space characters and does not strip horizontal tabs, even though RFC 7230 defines optional whitespace as both space and tab. As a result, an entry padded with a tab keeps the literal tab in the resolved address string. Applications that make exact string match security decisions on the resolved client IP, such as an allowlist, a blocklist, a per IP rate limit key, or audit log correlation, can be evaded because the tab corrupted string no longer matches the expected value. This does not cross the trust boundary, since a tab corrupted string is not a valid IP and cannot be mistaken for a trusted proxy. The issue is fixed in @fastify/forwarded 3.0.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18174.json
- https://github.com/fastify/forwarded/security/advisories/GHSA-2849-m2w7-xm8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-18174
