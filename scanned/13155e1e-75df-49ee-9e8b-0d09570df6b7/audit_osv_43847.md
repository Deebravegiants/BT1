# [M] Hugging Face Transformers Path Traversal via Checkpoint Index

## Summary
Severity: Medium
Advisory: CVE-2026-75104
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75104
Type: osv

## Details
Hugging Face Transformers fails to validate shard filenames in checkpoint index files, allowing attackers to read arbitrary files outside the model directory. Attackers can supply malicious index files with parent-directory references or absolute paths that are joined without validation, enabling file disclosure and filesystem reconnaissance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75104.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75104
- https://www.vulncheck.com/advisories/hugging-face-transformers-path-traversal-via-checkpoint-index
- https://github.com/huggingface/transformers/issues/47176
- https://github.com/huggingface/transformers/issues/47177
- https://github.com/huggingface/transformers
- https://github.com/huggingface/transformers/blob/main/src/transformers/utils/hub.py
