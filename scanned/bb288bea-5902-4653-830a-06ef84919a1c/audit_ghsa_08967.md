# [C] SGLang: Unauthenticated RCE via --enable-custom-logit-processor

## Summary
Severity: Critical
Advisory: GHSA-36m8-w8qf-g76p
CVE: CVE-2026-7304
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-36m8-w8qf-g76p
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0.4.1.post7

## Details
SGLang's multimodal generation runtime is vulnerable to unauthenticated remote code execution when the --enable-custom-logit-processor option is enabled, as Python objects loaded via dill.loads() will be deserialized without validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7304
- https://antiproof.ai/blog/three-rces-in-sglang
- https://github.com/sgl-project/sglang
- https://github.com/sgl-project/sglang/tree/main/python/sglang
