# [C] llama-index-core Prompt Injection vulnerability leading to Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-wvpx-g427-q9wc
CVE: CVE-2024-3098
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-wvpx-g427-q9wc
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.10.24

## Details
A vulnerability was identified in the `exec_utils` class of the `llama_index` package, specifically within the `safe_eval` function, allowing for prompt injection leading to arbitrary code execution. This issue arises due to insufficient validation of input, which can be exploited to bypass method restrictions and execute unauthorized code. The vulnerability is a bypass of the previously addressed CVE-2023-39662, demonstrated through a proof of concept that creates a file on the system by exploiting the flaw.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3098
- https://github.com/run-llama/llama_index/commit/2c92e88838a5f481d50840240b1dd3180066c6f5
- https://github.com/run-llama/llama_index/commit/5fbcb5a8b9f20f81b791c7fc8849e352613ab475
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/1bce0d61-ad03-4b22-bc32-8f99f92974e7
