# [M] HuggingFace Transformers allows for arbitrary code execution in the `Trainer` class

## Summary
Severity: Medium
Advisory: GHSA-69w3-r845-3855
CVE: CVE-2026-1839
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-69w3-r845-3855
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <5.0.0rc3

## Details
A vulnerability in the HuggingFace Transformers library, specifically in the `Trainer` class, allows for arbitrary code execution. The `_load_rng_state()` method in `src/transformers/trainer.py` at line 3059 calls `torch.load()` without the `weights_only=True` parameter. This issue affects all versions of the library supporting `torch>=2.2` when used with PyTorch versions below 2.6, as the `safe_globals()` context manager provides no protection in these versions. An attacker can exploit this vulnerability by supplying a malicious checkpoint file, such as `rng_state.pth`, which can execute arbitrary code when loaded. The issue is resolved in version v5.0.0rc3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1839
- https://github.com/huggingface/transformers/commit/03c8082ba4594c9b8d6fe190ca9bed0e5f8ca396
- https://github.com/huggingface/transformers
- https://github.com/huggingface/transformers/releases/tag/v5.0.0rc3
- https://huntr.com/bounties/3c77bb97-e493-493d-9a88-c57f5c536485
