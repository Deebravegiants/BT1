# [H] Multer vulnerable to Denial of Service via memory leaks from unclosed streams

## Summary
Severity: High
Advisory: GHSA-44fp-w29j-9vj5
CVE: CVE-2025-47935
CWE: CWE-401
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-44fp-w29j-9vj5
Type: github-advisory

## Affected
- npm: `multer` — affected >=0 <2.0.0

## Details
### Impact

Multer <2.0.0 is vulnerable to a resource exhaustion and memory leak issue due to improper stream handling. When the HTTP request stream emits an error, the internal `busboy` stream is not closed, violating Node.js stream safety guidance.

This leads to unclosed streams accumulating over time, consuming memory and file descriptors. Under sustained or repeated failure conditions, this can result in denial of service, requiring manual server restarts to recover. All users of Multer handling file uploads are potentially impacted.


### Patches

Users should upgrade to `2.0.0`


### Workarounds

None

### References

- https://github.com/expressjs/multer/pull/1120
- https://github.com/expressjs/multer/commit/2c8505f207d923dd8de13a9f93a4563e59933665

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-44fp-w29j-9vj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-47935
- https://github.com/expressjs/multer/pull/1120
- https://github.com/expressjs/multer/commit/2c8505f207d923dd8de13a9f93a4563e59933665
- https://github.com/expressjs/multer
