# [H] vllm API endpoints vulnerable to Denial of Service Attacks

## Summary
Severity: High
Advisory: GHSA-rxc4-3w6r-4v47
CVE: CVE-2025-48956
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-rxc4-3w6r-4v47
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.1.0 <0.10.1.1

## Details
### Summary
A Denial of Service (DoS) vulnerability can be triggered by sending a single HTTP GET request with an extremely large header to an HTTP endpoint. This results in server memory exhaustion, potentially leading to a crash or unresponsiveness. The attack does not require authentication, making it exploitable by any remote user.

### Details
The vulnerability leverages the abuse of HTTP headers. By setting a header such as `X-Forwarded-For` to a very large value like `("A" * 5_800_000_000)`, the server's HTTP parser or application logic may attempt to load the entire request into memory, overwhelming system resources.

### Impact
_What kind of vulnerability is it? Who is impacted?_
Type of vulnerability: Denial of Service (DoS)

### Resolution
Upgrade to a version of vLLM that includes appropriate HTTP limits by deafult, or use a proxy in front of vLLM which provides protection against this issue.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-rxc4-3w6r-4v47
- https://nvd.nist.gov/vuln/detail/CVE-2025-48956
- https://github.com/vllm-project/vllm/pull/23267
- https://github.com/vllm-project/vllm/commit/d8b736f913a59117803d6701521d2e4861701944
- https://github.com/advisories/GHSA-rxc4-3w6r-4v47
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2021.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
