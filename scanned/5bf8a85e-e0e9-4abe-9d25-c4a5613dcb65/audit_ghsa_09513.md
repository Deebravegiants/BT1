# [H] multiparty vulnerable to ReDoS via filename parsing

## Summary
Severity: High
Advisory: GHSA-65x3-rw7q-gx94
CVE: CVE-2026-8159
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-65x3-rw7q-gx94
Type: github-advisory

## Affected
- npm: `multiparty` — affected >=0 <4.3.0

## Details
### Impact

multiparty@4.2.3 and lower versions are vulnerable to denial of service via regular expression backtracking in the `Content-Disposition` filename parameter parser. A multipart upload with a long header value containing `!filename="1` repeated can cause regex matching to take seconds, blocking the event loop. Any service accepting multipart uploads via multiparty is affected.

### Patches

Users should upgrade to multiparty@4.3.0 or higher.

### Workarounds

None. Limiting upload sizes at the proxy/gateway layer reduces but does not eliminate the attack surface, since a small ~8 KB header is sufficient to trigger the vulnerable backtracking.

### Resources

- [OWASP: Regular expression Denial of Service (ReDoS)](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

## References
- https://github.com/pillarjs/multiparty/security/advisories/GHSA-65x3-rw7q-gx94
- https://nvd.nist.gov/vuln/detail/CVE-2026-8159
- https://cna.openjsf.org/security-advisories.html
- https://github.com/pillarjs/multiparty
- https://github.com/pillarjs/multiparty/releases/tag/v4.3.0
- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
