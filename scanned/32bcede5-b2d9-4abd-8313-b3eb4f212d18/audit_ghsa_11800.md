# [C] SGLang's multimodal generation module is vulnerable to unauthenticated remote code execution through the ZMQ broker

## Summary
Severity: Critical
Advisory: GHSA-rgq9-fqf5-fv58
CVE: CVE-2026-3059
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-rgq9-fqf5-fv58
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0 <0.5.10

## Details
SGLang's multimodal generation module is vulnerable to unauthenticated remote code execution through the ZMQ broker, which deserializes untrusted data using pickle.loads() without authentication.

## References
- https://github.com/sgl-project/sglang/security/advisories/GHSA-3cp7-c6q2-94xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-3059
- https://github.com/sgl-project/sglang/pull/20904
- https://github.com/sgl-project/sglang
- https://github.com/sgl-project/sglang/blob/main/python/sglang/multimodal_gen/runtime/scheduler_client.py
- https://github.com/sgl-project/sglang/releases/tag/v0.5.10
- https://orca.security/resources/blog/sglang-llm-framework-rce-vulnerabilities
