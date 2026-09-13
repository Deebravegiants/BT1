# [H] multer vulnerable to Denial of Service via file descriptor leak on aborted uploads

## Summary
Severity: High
Advisory: CVE-2026-77037
Aliases: GHSA-qfvm-cv95-jqjf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-77037
Type: osv

## Details
multer is a middleware for handling multipart/form-data in Node.js. In version 2.2.0, when a disk-backed upload is aborted or truncated before the write stream finishes, multer's disk storage engine removes the visible file but does not close the underlying write file descriptor, leaving a deleted but still open descriptor. A remote attacker able to reach an upload route using the built-in disk storage can send repeated aborted or malformed multipart uploads, each one leaking a file descriptor and retaining disk blocks until the process exits, which can exhaust resources and cause a denial of service. The issue is fixed in multer 2.3.0, which closes the destination write stream on abnormal source termination and defers cleanup until the stream has closed. Upgrade to multer 2.3.0 to remediate.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77037.json
- https://github.com/expressjs/multer/security/advisories/GHSA-qfvm-cv95-jqjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-77037
