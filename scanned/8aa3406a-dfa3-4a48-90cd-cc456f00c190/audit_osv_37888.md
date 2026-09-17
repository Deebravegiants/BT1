# [H] Chamilo LMS Affected by Authenticated Arbitrary File Write via BigUpload endpoint

## Summary
Severity: High
Advisory: CVE-2026-33704
Aliases: GHSA-phfx-pwwg-945v
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33704
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, any authenticated user (including students) can write arbitrary content to files on the server via the BigUpload endpoint. The key parameter controls the filename and the raw POST body becomes the file content. While .php extensions are filtered to .phps, the .pht extension passes through unmodified. On Apache configurations where .pht is handled as PHP, this leads to Remote Code Execution. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33704.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-phfx-pwwg-945v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33704
- https://github.com/chamilo/chamilo-lms/commit/9748f1ffbdb8b6dc84c0e0591c9d3c1d92e21c00
