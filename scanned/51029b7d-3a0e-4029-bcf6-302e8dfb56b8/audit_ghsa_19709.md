# [H] LlamaIndex Improper Handling of Exceptional Conditions vulnerability

## Summary
Severity: High
Advisory: GHSA-j3wr-m6xh-64hg
CVE: CVE-2024-12704
CWE: CWE-755, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-j3wr-m6xh-64hg
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.12.6

## Details
A vulnerability in the LangChainLLM class of the run-llama/llama_index repository, version v0.12.5, allows for a Denial of Service (DoS) attack. The stream_complete method executes the llm using a thread and retrieves the result via the get_response_gen method of the StreamingGeneratorCallbackHandler class. If the thread terminates abnormally before the _llm.predict is executed, there is no exception handling for this case, leading to an infinite loop in the get_response_gen function. This can be triggered by providing an input of an incorrect type, causing the thread to terminate and the process to continue running indefinitely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12704
- https://github.com/run-llama/llama_index/commit/d1ecfb77578d089cbe66728f18f635c09aa32a05
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/a0b638fd-21c6-4ba7-b381-6ab98472a02a
