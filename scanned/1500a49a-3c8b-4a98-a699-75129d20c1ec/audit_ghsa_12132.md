# [H] Multer vulnerable to Denial of Service via resource exhaustion

## Summary
Severity: High
Advisory: GHSA-v52c-386h-88mc
CVE: CVE-2026-2359
CWE: CWE-772
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-v52c-386h-88mc
Type: github-advisory

## Affected
- npm: `multer` — affected >=0 <2.1.0

## Details
### Impact

A vulnerability in Multer versions < 2.1.0 allows an attacker to trigger a Denial of Service (DoS) by dropping connection during file upload, potentially causing resource exhaustion.

### Patches

Users should upgrade to `2.1.0`

### Workarounds

None

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-v52c-386h-88mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-2359
- https://github.com/expressjs/multer/commit/cccf0fe0e64150c4f42ccf6654165c0d66b9adab
- https://cna.openjsf.org/security-advisories.html
- https://github.com/expressjs/multer
- https://www.cve.org/CVERecord?id=CVE-2026-2359
