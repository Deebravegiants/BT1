# [C] Langchain OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x32c-59v5-h7fg
CVE: CVE-2023-34540
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-x32c-59v5-h7fg
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0 <0.0.225

## Details
Langchain before v0.0.225 was discovered to contain a remote code execution (RCE) vulnerability in the component JiraAPIWrapper (aka the JIRA API wrapper). This vulnerability allows attackers to execute arbitrary code via crafted input. As noted in the "releases/tag" reference, a fix is available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34540
- https://github.com/hwchase17/langchain/issues/4833
- https://github.com/langchain-ai/langchain/issues/4833
- https://github.com/langchain-ai/langchain/pull/6992
- https://github.com/langchain-ai/langchain/commit/a2f191a32229256dd41deadf97786fe41ce04cbb
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/releases/tag/v0.0.225
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain/PYSEC-2023-91.yaml
