# [H] RAGAS has an Arbitrary File Read vulnerability

## Summary
Severity: High
Advisory: GHSA-v2xr-wvrv-p969
CVE: CVE-2025-45691
CWE: CWE-22, CWE-770, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-v2xr-wvrv-p969
Type: github-advisory

## Affected
- PyPI: `ragas` — affected >=0.2.3 <0.3.0-rc1

## Details
An Arbitrary File Read vulnerability exists in the ImageTextPromptValue class in Exploding Gradients RAGAS v0.2.3 to v0.2.14. The vulnerability stems from improper validation and sanitization of URLs supplied in the retrieved_contexts parameter when handling multimodal inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-45691
- https://github.com/explodinggradients/ragas/pull/1559
- https://github.com/vibrantlabsai/ragas/pull/1991
- https://github.com/vibrantlabsai/ragas/commit/b28433709cbedbb531db79dadcfbdbd3aa6adcb0
- https://adithyanak.com/ragas-v0214-arbitrary-file-read-vulnerability
- https://github.com/explodinggradients/ragas/blob/e97886ac976465efb60e5949c5d69baf30cc811d/src/ragas/prompt/multi_modal_prompt.py#L202
- https://github.com/vibrantlabsai/ragas
