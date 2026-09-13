# [M] Denial of Service by abusing xgrammar unbounded cache in memory

## Summary
Severity: Medium
Advisory: CVE-2025-32381
Aliases: GHSA-389x-67px-mjg3, PYSEC-2025-235
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-09
Source: https://osv.dev/vulnerability/CVE-2025-32381
Type: osv

## Details
XGrammar is an open-source library for efficient, flexible, and portable structured generation. Prior to 0.1.18, Xgrammar includes a cache for compiled grammars to increase performance with repeated use of the same grammar. This cache is held in memory. Since the cache is unbounded, a system making use of xgrammar can be abused to fill up a host's memory and case a denial of service. For example, sending many small requests to an LLM inference server with unique JSON schemas would eventually cause this denial of service to occur. This vulnerability is fixed in 0.1.18.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32381.json
- https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-389x-67px-mjg3
- https://nvd.nist.gov/vuln/detail/CVE-2025-32381
- https://github.com/mlc-ai/xgrammar/pull/243
- https://github.com/vllm-project/vllm/pull/16283
