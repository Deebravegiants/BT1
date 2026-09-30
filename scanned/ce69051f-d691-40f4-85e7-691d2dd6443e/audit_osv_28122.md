# [H] CVE-2024-28088

## Summary
Severity: High
Advisory: CVE-2024-28088
Aliases: GHSA-h59x-p739-982c, PYSEC-2024-43, PYSEC-2024-45
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-03
Source: https://osv.dev/vulnerability/CVE-2024-28088
Type: osv

## Details
LangChain through 0.1.10 allows ../ directory traversal by an actor who is able to control the final part of the path parameter in a load_chain call. This bypasses the intended behavior of loading configurations only from the hwchase17/langchain-hub GitHub repository. The outcome can be disclosure of an API key for a large language model online service, or remote code execution. (A patch is available as of release 0.1.29 of langchain-core.)

## References
- https://github.com/PinkDraconian/PoC-Langchain-RCE/blob/main/README.md
- https://github.com/langchain-ai/langchain/blob/f96dd57501131840b713ed7c2e86cbf1ddc2761f/libs/core/langchain_core/utils/loading.py
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28088.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28088
- https://github.com/langchain-ai/langchain/pull/18600
