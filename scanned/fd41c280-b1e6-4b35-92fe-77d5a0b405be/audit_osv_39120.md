# [M] Algernon: Path traversal file write via savein()

## Summary
Severity: Medium
Advisory: CVE-2026-43982
Aliases: GHSA-2j2c-pv62-mmcp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43982
Type: osv

## Details
Algernon is a small self-contained pure-Go web server. Prior to 1.17.6, uploadedFileSaveIn() in lua/upload/upload.go uses filepath.Join() with the caller-supplied directory but performs no boundary check after joining. A directory of ../../../tmp resolves cleanly to /tmp, outside the web root. This vulnerability is fixed in 1.17.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43982.json
- https://github.com/xyproto/algernon/security/advisories/GHSA-2j2c-pv62-mmcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-43982
- https://github.com/xyproto/algernon/issues/172
