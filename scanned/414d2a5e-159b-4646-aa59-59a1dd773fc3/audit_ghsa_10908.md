# [C] SGLang's encoder parallel disaggregation system is vulnerable to unauthenticated remote code execution through the disaggregation module

## Summary
Severity: Critical
Advisory: GHSA-jx93-g359-86wm
CVE: CVE-2026-3060
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-jx93-g359-86wm
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0 <0.5.10

## Details
SGLang's encoder parallel disaggregation system is vulnerable to unauthenticated remote code execution through the disaggregation module, which deserializes untrusted data using pickle.loads() without authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3060
- https://github.com/sgl-project/sglang/pull/20904
- https://github.com/sgl-project/sglang
- https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/disaggregation/encode_receiver.py
- https://github.com/sgl-project/sglang/releases/tag/v0.5.10
- https://orca.security/resources/blog/sglang-llm-framework-rce-vulnerabilities
