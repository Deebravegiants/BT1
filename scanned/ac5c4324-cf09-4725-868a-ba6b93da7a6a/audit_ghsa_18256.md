# [H] llama-index-core insecurely handles temporary files

## Summary
Severity: High
Advisory: GHSA-cr7q-2w66-hjcm
CVE: CVE-2025-7647
CWE: CWE-378
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-09-27
Source: https://github.com/advisories/GHSA-cr7q-2w66-hjcm
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.13.0

## Details
The llama-index-core package, up to version 0.12.44, contains a vulnerability in the `get_cache_dir()` function where a predictable, hardcoded directory path `/tmp/llama_index` is used on Linux systems without proper security controls. This vulnerability allows attackers on multi-user systems to steal proprietary models, poison cached embeddings, or conduct symlink attacks. The issue affects all Linux deployments where multiple users share the same system. The vulnerability is classified under CWE-379, CWE-377, and CWE-367, indicating insecure temporary file creation and potential race conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7647
- https://github.com/run-llama/llama_index/commit/98816394d57c7f53f847ed7b60725e69d0e7aae4
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/a2baa08f-98bf-47a8-ac83-06f7411afd9e
