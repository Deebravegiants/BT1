# [H] Multer vulnerable to Denial of Service from maliciously crafted requests

## Summary
Severity: High
Advisory: GHSA-4pg4-qvpc-4q3h
CVE: CVE-2025-47944
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-4pg4-qvpc-4q3h
Type: github-advisory

## Affected
- npm: `multer` — affected >=1.4.4-lts.1 <2.0.0

## Details
### Impact
A vulnerability in Multer versions >=1.4.4-lts.1 allows an attacker to trigger a Denial of Service (DoS) by sending a malformed multi-part upload request. This request causes an unhandled exception, leading to a crash of the process.

### Patches
Users should upgrade to `2.0.0`

### Workarounds
None

### References

- https://github.com/expressjs/multer/issues/1176
- https://github.com/expressjs/multer/commit/2c8505f207d923dd8de13a9f93a4563e59933665

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-4pg4-qvpc-4q3h
- https://nvd.nist.gov/vuln/detail/CVE-2025-47944
- https://github.com/expressjs/multer/issues/1176
- https://github.com/expressjs/multer/commit/2c8505f207d923dd8de13a9f93a4563e59933665
- https://github.com/expressjs/multer
