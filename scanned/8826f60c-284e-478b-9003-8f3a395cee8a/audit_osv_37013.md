# [H] Zed has Zip Slip Path Traversal in Extension Archive Extraction

## Summary
Severity: High
Advisory: CVE-2026-27800
Aliases: GHSA-v385-xh3h-rrfr
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27800
Type: osv

## Details
Zed, a code editor, has a Zip Slip (Path Traversal) vulnerability exists in its extension archive extraction functionality prior to version 0.224.4. The `extract_zip()` function in `crates/util/src/archive.rs` fails to validate ZIP entry filenames for path traversal sequences (e.g., `../`). This allows a malicious extension to write files outside its designated sandbox directory by downloading and extracting a crafted ZIP archive. Version 0.224.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27800.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-v385-xh3h-rrfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27800
