# [H] Hugging Face Accelerate 1.14.0 Path Traversal and DoS via weight_map

## Summary
Severity: High
Advisory: CVE-2026-69112
Aliases: GHSA-4j2p-28q2-5m79, PYSEC-2026-3804
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-69112
Type: osv

## Details
Hugging Face Accelerate through 1.14.0 contains a path traversal vulnerability in load_checkpoint_in_model and load_checkpoint_and_dispatch functions that fail to sanitize weight_map entries from sharded checkpoint indexes. Attackers can supply relative paths with ../ sequences or absolute paths to read arbitrary files, or point shard entries at named pipes to cause indefinite blocking and denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69112.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69112
- https://www.vulncheck.com/advisories/hugging-face-accelerate-path-traversal-and-dos-via-weight-map
- https://github.com/huggingface/accelerate/pull/4070
- https://github.com/huggingface/accelerate/pull/4138
- https://github.com/huggingface/accelerate
- https://github.com/huggingface/accelerate/issues/4067
