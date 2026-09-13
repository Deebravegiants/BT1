# [C] SGLanG: Multimodal scheduler deserializes untrusted pickle data on 0.0.0.0 ROUTER socket

## Summary
Severity: Critical
Advisory: GHSA-gwv6-pq6m-p3rq
CVE: CVE-2026-7301
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-gwv6-pq6m-p3rq
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0.5.5

## Details
SGLang's multimodal generation runtime scheduler's ROUTER socket binds to 0.0.0.0 by default and contains a sink that calls pickle.loads() on incoming messages, enabling RCE when exposed to the internet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7301
- https://antiproof.ai/blog/three-rces-in-sglang
- https://github.com/sgl-project/sglang
- https://github.com/sgl-project/sglang/tree/main/python/sglang
