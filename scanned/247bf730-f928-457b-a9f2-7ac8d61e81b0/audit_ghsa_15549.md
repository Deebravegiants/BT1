# [H] LangChain pickle deserialization of untrusted data

## Summary
Severity: High
Advisory: GHSA-f2jm-rw3h-6phg
CVE: CVE-2024-5998
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-f2jm-rw3h-6phg
Type: github-advisory

## Affected
- PyPI: `langchain-community` — affected >=0 <0.2.4

## Details
A vulnerability in the `FAISS.deserialize_from_bytes` function of langchain-ai/langchain allows for pickle deserialization of untrusted data. This can lead to the execution of arbitrary commands via the `os.system` function. The issue affects versions prior to 0.2.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5998
- https://github.com/langchain-ai/langchain/commit/604dfe2d99246b0c09f047c604f0c63eafba31e7
- https://github.com/langchain-ai/langchain/commit/77209f315efd13442ec51c67719ba37dfaa44511
- https://github.com/langchain-ai/langchain
- https://huntr.com/bounties/fa3a2753-57c3-4e08-a176-d7a3ffda28fe
