# [H] vLLM is vulnerable to an Out-of-Memory (OOM) Denial of Service (DoS) attack due to unbounded frame count processing in the `VideoMediaIO.load_base64()` method

## Summary
Severity: High
Advisory: GHSA-wcwg-c5fc-9vrc
CVE: CVE-2026-5497
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-wcwg-c5fc-9vrc
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.8.0 <0.19.0

## Details
vLLM versions 0.8.0 and later are vulnerable to an Out-of-Memory (OOM) Denial of Service (DoS) attack due to unbounded frame count processing in the `VideoMediaIO.load_base64()` method. When processing `video/jpeg` data URLs, the method splits the base64 data string on commas to extract individual JPEG frames without enforcing a frame count limit. An attacker can exploit this by crafting a single API request containing thousands of comma-separated base64-encoded JPEG frames in a data URL, causing the server to decode all frames into memory and crash due to excessive memory consumption. This vulnerability is reachable via the OpenAI-compatible chat completions API and does not require authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5497
- https://github.com/vllm-project/vllm/commit/58ee61422169ce17e08248f8efa1e9df434fe395
- https://access.redhat.com/errata/RHSA-2026:33524
- https://access.redhat.com/errata/RHSA-2026:33531
- https://access.redhat.com/security/cve/CVE-2026-5497
- https://bugzilla.redhat.com/show_bug.cgi?id=2487813
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2302.yaml
- https://github.com/vllm-project/vllm
- https://huntr.com/bounties/7bd92629-b396-4449-8f88-6c0092530eb4
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-5497.json
