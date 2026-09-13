# [C] LangChain vulnerable to code injection

## Summary
Severity: Critical
Advisory: GHSA-fprp-p869-w6q2
CVE: CVE-2023-29374
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-fprp-p869-w6q2
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0

## Details
In LangChain through 0.0.131, the `LLMMathChain` chain allows prompt injection attacks that can execute arbitrary code via the Python `exec()` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29374
- https://github.com/hwchase17/langchain/issues/1026
- https://github.com/hwchase17/langchain/issues/814
- https://github.com/hwchase17/langchain/pull/1119
- https://github.com/langchain-ai/langchain
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain/PYSEC-2023-18.yaml
- https://twitter.com/rharang/status/1641899743608463365/photo/1
