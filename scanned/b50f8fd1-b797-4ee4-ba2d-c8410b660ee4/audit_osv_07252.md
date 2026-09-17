# [M] Parse Server has a file upload Content-Type override via extension mismatch

## Summary
Severity: Medium
Advisory: BIT-parse-2026-35200
Aliases: CVE-2026-35200, GHSA-vr5f-2r24-w5hc
Ecosystem: Bitnami
Published: 2026-04-08
Source: https://osv.dev/vulnerability/BIT-parse-2026-35200
Type: osv

## Affected
- Bitnami: `parse` — affected >=9.0.0 <9.7.1

## Details
Parse Server is an open source backend that can be deployed to any infrastructure that can run Node.js. Prior to 8.6.73 and 9.7.1, a file can be uploaded with a filename extension that passes the file extension allowlist (e.g., .txt) but with a Content-Type header that differs from the extension (e.g., text/html). The Content-Type is passed to the storage adapter without consistency validation. Storage adapters that store and serve the provided Content-Type (such as S3 or GCS) serve the file with the mismatched Content-Type. The default GridFS adapter is not affected because it derives Content-Type from the filename at serving time. This vulnerability is fixed in 8.6.73 and 9.7.1.

## References
- https://github.com/parse-community/parse-server/pull/10383
- https://github.com/parse-community/parse-server/pull/10384
- https://github.com/parse-community/parse-server/security/advisories/GHSA-vr5f-2r24-w5hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35200
