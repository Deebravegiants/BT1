# [M] SGLang has an Improper Input Validation/Injection Issue

## Summary
Severity: Medium
Advisory: GHSA-6m5f-673f-5vh7
CVE: CVE-2026-7669
CWE: CWE-20, CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-03
Source: https://github.com/advisories/GHSA-6m5f-673f-5vh7
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0

## Details
A vulnerability was detected in sgl-project SGLang up to 0.5.9. Impacted is the function get_tokenizer of the file python/sglang/srt/utils/hf_transformers_utils.py of the component HuggingFace Transformer Handler. The manipulation results in deserialization. The attack can be executed remotely. A high complexity level is associated with this attack. The exploitability is considered difficult. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7669
- https://github.com/gouldnicholas/CVE-2026-7669-PoC
- https://github.com/sgl-project/sglang
- https://vuldb.com/submit/799263
- https://vuldb.com/vuln/360817
- https://vuldb.com/vuln/360817/cti
