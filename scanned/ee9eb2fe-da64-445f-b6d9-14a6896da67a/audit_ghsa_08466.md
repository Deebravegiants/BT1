# [H] multiparty vulnerable to Denial of Service via Uncaught Exception in filename* parameter parsing

## Summary
Severity: High
Advisory: GHSA-xh3c-6gcq-g4rv
CVE: CVE-2026-8162
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-xh3c-6gcq-g4rv
Type: github-advisory

## Affected
- npm: `multiparty` — affected >=0 <4.3.0

## Details
### Impact

multiparty@4.2.3 and lower versions are vulnerable to denial of service via uncaught exception. By sending a `multipart/form-data` request with a `Content-Disposition: filename*=utf-8''` header containing a malformed percent-encoding (e.g., `%FF`, `%GG`), the parser invokes `decodeURI` on the value without try/catch. The resulting `URIError` propagates as an uncaught exception and crashes the process. Any service accepting multipart uploads via multiparty is affected.

### Patches

Users should upgrade to multiparty@4.3.0 or higher.

### Workarounds

None.

## References
- https://github.com/pillarjs/multiparty/security/advisories/GHSA-xh3c-6gcq-g4rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-8162
- https://cna.openjsf.org/security-advisories.html
- https://github.com/pillarjs/multiparty
- https://github.com/pillarjs/multiparty/releases/tag/v4.3.0
