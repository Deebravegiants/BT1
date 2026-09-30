# [C] SGLang's multimodal generation runtime has an unauthenticated path traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qwrp-wghp-94q2
CVE: CVE-2026-7302
CWE: CWE-35
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-qwrp-wghp-94q2
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0.5.5

## Details
SGLang's multimodal generation runtime is vulnerable to an unauthenticated path traversal vulnerability, allowing an attacker to write arbitrary files anywhere the server process has write access, by including ../ sequences in the upload filename when sent to specific endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7302
- https://antiproof.ai/blog/three-rces-in-sglang
- https://github.com/sgl-project/sglang
- https://github.com/sgl-project/sglang/tree/main/python/sglang
