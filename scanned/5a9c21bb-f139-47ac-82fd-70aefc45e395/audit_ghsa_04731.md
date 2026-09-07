# [M] Multer vulnerable to Denial of Service via incomplete cleanup of aborted uploads

## Summary
Severity: Medium
Advisory: GHSA-3p4h-7m6x-2hcm
CVE: CVE-2026-5038
CWE: CWE-459
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-3p4h-7m6x-2hcm
Type: github-advisory

## Affected
- npm: `multer` — affected >=2.0.0-alpha.1 <2.2.0
- npm: `multer` — affected >=3.0.0-alpha.1 <3.0.0-alpha.2

## Details
### Impact

A vulnerability in Multer allows an attacker to trigger a Denial of Service (DoS) by aborting or sending malformed multipart uploads, causing orphaned partial files to accumulate on disk when using diskStorage.

### Patches

Users should upgrade to `2.2.0`, `3.0.0-alpha.2` or higher

### Workarounds

None

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-3p4h-7m6x-2hcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-5038
- https://cna.openjsf.org/security-advisories.html
- https://github.com/expressjs/multer
