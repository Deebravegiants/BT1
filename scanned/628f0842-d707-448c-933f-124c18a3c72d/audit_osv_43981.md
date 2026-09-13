# [H] multer vulnerable to Denial of Service via crafted multipart field names

## Summary
Severity: High
Advisory: CVE-2026-77078
Aliases: GHSA-wc9g-mqfw-jrwm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-77078
Type: osv

## Details
multer is a middleware for handling multipart/form-data in Node.js. A small multipart request containing two specially crafted text field names can cause an uncaught RangeError (Invalid array length) that terminates the Node.js process. The first field uses a very large numeric array index to allocate a maximum-length sparse array, and a second field then pushes past that length, which throws inside the append-field dependency and is not caught by multer. All versions before 2.3.0 are affected, and the issue is a remotely triggerable denial of service. The issue is fixed in multer 2.3.0. Upgrade to multer 2.3.0 to remediate.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77078.json
- https://github.com/expressjs/multer/security/advisories/GHSA-wc9g-mqfw-jrwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-77078
