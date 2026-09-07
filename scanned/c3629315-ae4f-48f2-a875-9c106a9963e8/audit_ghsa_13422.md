# [H] langchain SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7q94-qpjr-xpgm
CVE: CVE-2023-36189
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-7q94-qpjr-xpgm
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0 <0.0.247

## Details
SQL injection vulnerability in langchain allows a remote attacker to obtain sensitive information via the SQLDatabaseChain component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36189
- https://github.com/hwchase17/langchain/issues/5923
- https://github.com/langchain-ai/langchain/issues/5923
- https://github.com/langchain-ai/langchain/issues/5923#issuecomment-1696053841
- https://github.com/hwchase17/langchain/pull/6051
- https://github.com/langchain-ai/langchain/pull/8425
- https://github.com/langchain-ai/langchain/commit/fab24457bcf8ede882abd11419769c92bc4e7751
- https://gist.github.com/rharang/9c58d39db8c01db5b7c888e467c0533f
- https://github.com/langchain-ai/langchain
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain/PYSEC-2023-110.yaml
