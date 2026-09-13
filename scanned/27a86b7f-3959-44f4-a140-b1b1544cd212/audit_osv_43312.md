# [M] kkFileView: Unauthenticated path traversal in POST /listFiles allows arbitrary directory listing

## Summary
Severity: Medium
Advisory: CVE-2026-73244
Aliases: GHSA-pmp8-g8p2-p6jq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73244
Type: osv

## Details
kkFileView is a universal file online preview project based on Spring Boot. Prior to 5.0.1, the unauthenticated POST /listFiles endpoint in server/src/main/java/cn/keking/web/controller/FileController.java passes the user-controlled path parameter from FileController#getFiles to Files.newDirectoryStream without confinement to the demo directory, allowing directory enumeration outside the intended root. This issue is fixed in version 5.0.1.

## References
- https://github.com/kekingcn/kkFileView/releases/tag/v5.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73244.json
- https://github.com/kekingcn/kkFileView/security/advisories/GHSA-pmp8-g8p2-p6jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73244
- https://github.com/kekingcn/kkFileView/commit/47745e4d74112000fcc4f0664e2fc751e6cf9bae
