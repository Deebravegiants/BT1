# [M] Datasets Path Traversal via Unsanitized file_name Metadata

## Summary
Severity: Medium
Advisory: CVE-2026-66007
Aliases: PYSEC-2026-3716
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66007
Type: osv

## Details
Datasets through 5.0.0, fixed in commit f989ef9, contains a path traversal vulnerability in folder-based dataset builders where the file_name metadata field is not properly validated before being joined to the dataset directory. Attackers can supply crafted file_name values with directory traversal sequences to read arbitrary local files, which are then embedded into output when save_to_disk or push_to_hub is called.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66007.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66007
- https://www.vulncheck.com/advisories/datasets-path-traversal-via-unsanitized-file-name-metadata
- https://github.com/huggingface/datasets/issues/8324
- https://github.com/huggingface/datasets/commit/f989ef9b4cc6c0039a7a82458eebca49e2b58b4b
- https://github.com/huggingface/datasets/pull/8325
- https://github.com/huggingface/datasets
