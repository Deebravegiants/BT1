# [H] Multer Vulnerable to Denial of Service via Uncontrolled Recursion

## Summary
Severity: High
Advisory: GHSA-5528-5vmv-3xc2
CVE: CVE-2026-3520
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-5528-5vmv-3xc2
Type: github-advisory

## Affected
- npm: `multer` — affected >=0 <2.1.1

## Details
### Impact

A vulnerability in Multer versions < 2.1.1 allows an attacker to trigger a Denial of Service (DoS) by sending malformed requests, potentially causing stack overflow.

### Patches

Users should upgrade to `2.1.1`

### Workarounds

None

### Resources

- https://github.com/expressjs/multer/security/advisories/GHSA-5528-5vmv-3xc2
- https://www.cve.org/CVERecord?id=CVE-2026-3520
- https://github.com/expressjs/multer/commit/7e66481f8b2e6c54b982b34c152479e096ce2752
- https://cna.openjsf.org/security-advisories.html

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-5528-5vmv-3xc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-3520
- https://github.com/expressjs/multer/commit/7e66481f8b2e6c54b982b34c152479e096ce2752
- https://cna.openjsf.org/security-advisories.html
- https://github.com/expressjs/multer
- https://www.cve.org/CVERecord?id=CVE-2026-3520
