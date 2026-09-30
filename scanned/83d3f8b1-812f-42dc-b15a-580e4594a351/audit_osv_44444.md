# [H] multer vulnerable to Denial of Service via oversized array index in field names

## Summary
Severity: High
Advisory: CVE-2026-82333
Aliases: GHSA-535w-7cp7-47q4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82333
Type: osv

## Details
multer is a middleware for handling multipart/form-data in Node.js. A small multipart request with two specially crafted text field names can make multer's field parser synchronously iterate a maximum-length sparse array, blocking the event loop so the process cannot handle other requests. A large numeric array index in the first field allocates a maximum-length sparse array, and a second field with a non-numeric key then triggers a full-length iteration inside the append-field dependency. All versions before 2.3.0 are affected, and this is a remotely triggerable denial of service. multer 2.3.0 adds an opt-in fieldArrayIndexLimit option that rejects oversized array indexes. Upgrade to multer 2.3.0 and set limits.fieldArrayIndexLimit to the largest array index your application needs to remediate.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82333.json
- https://github.com/expressjs/multer/security/advisories/GHSA-535w-7cp7-47q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-82333
