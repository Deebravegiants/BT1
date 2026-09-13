# [H] vLLM denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-w2r7-9579-27hf
CVE: CVE-2024-8768
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-w2r7-9579-27hf
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.5.5

## Details
A flaw was found in the vLLM library. A completions API request with an empty prompt will crash the vLLM API server, resulting in a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8768
- https://github.com/vllm-project/vllm/issues/7632
- https://github.com/vllm-project/vllm/pull/7746
- https://github.com/vllm-project/vllm/commit/e25fee57c2e69161bd261f5986dc5aeb198bbd42
- https://access.redhat.com/security/cve/CVE-2024-8768
- https://bugzilla.redhat.com/show_bug.cgi?id=2311895
- https://github.com/vllm-project/vllm
