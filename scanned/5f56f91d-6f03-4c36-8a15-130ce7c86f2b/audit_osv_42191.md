# [H] Datasets Symlink-following Arbitrary File Write via Extractor.extract()

## Summary
Severity: High
Advisory: CVE-2026-65010
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65010
Type: osv

## Details
Datasets through 5.00, fixed in commit ad2d853, contains a symlink-following vulnerability in Extractor.extract() that allows local attackers to write arbitrary files by pre-planting symlinks at predictable output paths. Attackers can redirect archive extraction to arbitrary filesystem locations in shared-cache environments, enabling overwrite of sensitive files and potential privilege escalation or code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65010.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65010
- https://www.vulncheck.com/advisories/datasets-symlink-following-arbitrary-file-write-via-extractor-extract
- https://github.com/huggingface/datasets/issues/8296
- https://github.com/huggingface/datasets/commit/ad2d853ae2ce41d8068c23b44c2e29004312ccee
- https://github.com/huggingface/datasets/pull/8303
- https://github.com/huggingface/datasets
