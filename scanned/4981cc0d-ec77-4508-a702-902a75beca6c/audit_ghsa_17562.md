# [H] Multer vulnerable to Denial of Service via unhandled exception

## Summary
Severity: High
Advisory: GHSA-g5hg-p3ph-g8qg
CVE: CVE-2025-48997
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-g5hg-p3ph-g8qg
Type: github-advisory

## Affected
- npm: `multer` — affected >=1.4.4-lts.1 <2.0.1

## Details
### Impact

A vulnerability in Multer versions >=1.4.4-lts.1, <2.0.1 allows an attacker to trigger a Denial of Service (DoS) by sending an upload file request with an empty string field name. This request causes an unhandled exception, leading to a crash of the process.

### Patches

Users should upgrade to `2.0.1`

### Workarounds

None

### References

https://github.com/expressjs/multer/commit/35a3272b611945155e046dd5cef11088587635e9
https://github.com/expressjs/multer/issues/1233
https://github.com/expressjs/multer/pull/1256

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-g5hg-p3ph-g8qg
- https://nvd.nist.gov/vuln/detail/CVE-2025-48997
- https://github.com/expressjs/multer/issues/1233
- https://github.com/expressjs/multer/pull/1256
- https://github.com/expressjs/multer/commit/35a3272b611945155e046dd5cef11088587635e9
- https://github.com/expressjs/multer
