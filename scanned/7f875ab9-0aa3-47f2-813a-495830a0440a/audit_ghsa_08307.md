# [H] multiparty: Denial of Service via Prototype Pollution leads to Uncaught Exception

## Summary
Severity: High
Advisory: GHSA-qxch-whhj-8956
CVE: CVE-2026-8161
CWE: CWE-1321, CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-qxch-whhj-8956
Type: github-advisory

## Affected
- npm: `multiparty` — affected >=0 <4.3.0

## Details
### Impact

multiparty@4.2.3 and lower versions are vulnerable to denial of service via uncaught exception. By sending a `multipart/form-data` request with a field name that collides with an inherited `Object.prototype` property (e.g., `__proto__`, `constructor`, `toString`), the parser invokes `.push()` on the inherited prototype value rather than an array, throwing a `TypeError` that propagates as an uncaught exception and crashes the process. Any service accepting multipart uploads via multiparty is affected.

### Patches

Users should upgrade to multiparty@4.3.0 or higher.

### Workarounds

None.

## References
- https://github.com/pillarjs/multiparty/security/advisories/GHSA-qxch-whhj-8956
- https://nvd.nist.gov/vuln/detail/CVE-2026-8161
- https://cna.openjsf.org/security-advisories.html
- https://github.com/pillarjs/multiparty
- https://github.com/pillarjs/multiparty/releases/tag/v4.3.0
