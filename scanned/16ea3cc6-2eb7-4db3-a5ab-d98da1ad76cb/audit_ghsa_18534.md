# [M] LlamaIndex has Incomplete Documentation of Program Execution related to JsonPickleSerializer component

## Summary
Severity: Medium
Advisory: GHSA-m84c-4c34-28gf
CVE: CVE-2025-3108
CWE: CWE-1112
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-m84c-4c34-28gf
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0.11.15 <0.12.41

## Details
Incomplete Documentation of Program Execution exists in the run-llama/llama_index library's JsonPickleSerializer component, affecting versions v0.12.27 through v0.12.40. This vulnerability allows remote code execution due to an insecure fallback to Python's pickle module. JsonPickleSerializer prioritizes deserialization using pickle.loads(), which can execute arbitrary code when processing untrusted data. Attackers can exploit this by crafting malicious payloads to achieve full system compromise. The root cause involves the use of an insecure fallback strategy without sufficient input validation or protective safeguards. Version 0.12.41 renames JsonPickleSerializer to PickleSerializer and adds a warning to the docs to only use PickleSerializer to deserialize safe things.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3108
- https://github.com/run-llama/llama_index/commit/702e4340623092fac4cf2fe95eb9465034856da3
- https://github.com/run-llama/llama_index
- https://github.com/run-llama/llama_index/blob/v0.12.41/CHANGELOG.md#llama-index-core-01241
- https://huntr.com/bounties/9b55a5e8-74e6-4241-b323-e360dc8b110a
