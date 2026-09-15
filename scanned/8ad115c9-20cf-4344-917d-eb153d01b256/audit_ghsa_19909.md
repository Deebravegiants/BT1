# [M] langchain-core allows unauthorized users to read arbitrary files from the host file system

## Summary
Severity: Medium
Advisory: GHSA-5chr-fjjv-38qv
CVE: CVE-2024-10940
CWE: CWE-497
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5chr-fjjv-38qv
Type: github-advisory

## Affected
- PyPI: `langchain-core` — affected >=0.1.17 <0.1.53
- PyPI: `langchain-core` — affected >=0.2.0 <0.2.43
- PyPI: `langchain-core` — affected >=0.3.0 <0.3.15

## Details
A vulnerability in langchain-core versions >=0.1.17,<0.1.53, >=0.2.0,<0.2.43, and >=0.3.0,<0.3.15 allows unauthorized users to read arbitrary files from the host file system. The issue arises from the ability to create langchain_core.prompts.ImagePromptTemplate's (and by extension langchain_core.prompts.ChatPromptTemplate's) with input variables that can read any user-specified path from the server file system. If the outputs of these prompt templates are exposed to the user, either directly or through downstream model outputs, it can lead to the exposure of sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10940
- https://github.com/langchain-ai/langchain/commit/7d481f10102f43559cc57bcad7eba291067939ee
- https://github.com/langchain-ai/langchain/commit/c1e742347f9701aadba8920e4d1f79a636e50b68
- https://github.com/langchain-ai/langchain/commit/e711034713259ae448981bc0fd1d7a5671499c31
- https://github.com/langchain-ai/langchain
- https://huntr.com/bounties/be1ee1cb-2147-4ff4-a57b-b6045271cf27
