# [H] Hugging Face Transformers library writes remote code to disk prior to consent check

## Summary
Severity: High
Advisory: CVE-2026-80047
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-80047
Type: osv

## Details
A vulnerability in Hugging Face Transformers (versions >= 4.49.0 and <= 5.8.1) allows remote Python files to be written to local disk without user consent when using GenerativePreTrainedModel.load_custom_generate(). The function fetches and caches a remote module file before performing the required trust_remote_code consent check, inverting the security model enforced by other code-loading paths (such as AutoConfig, AutoModel, and AutoTokenizer). As a result, attacker‑controlled Python code from custom_generate/generate.py is copied into the user’s ~/.cache/huggingface/modules directory even if the user declines the trust prompt. Although execution is correctly gated, the file write is not reversible and can persist across sessions. This can lead to persistent, unauthorized files on disk and stale cache collisions where cached attacker code may later be executed during trusted model loads. The issue stems from an unconditional file write in dynamic_module_utils.py prior to any trust verification.

## References
- https://kb.cert.org/vuls/id/456290
- https://www.kb.cert.org/vuls/id/456290
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80047.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80047
- https://github.com/huggingface/transformers
