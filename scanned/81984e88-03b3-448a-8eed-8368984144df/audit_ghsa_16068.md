# [H] Deserialization of Untrusted Data in Hugging Face Transformers

## Summary
Severity: High
Advisory: GHSA-wrfc-pvp9-mr9g
CVE: CVE-2024-11393
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-23
Source: https://github.com/advisories/GHSA-wrfc-pvp9-mr9g
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.48.0

## Details
Hugging Face Transformers MaskFormer Model Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Hugging Face Transformers. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of model files. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-25191.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11393
- https://github.com/huggingface/transformers/issues/34840
- https://github.com/huggingface/transformers/pull/35296
- https://github.com/huggingface/transformers
- https://github.com/pypa/advisory-database/tree/main/vulns/transformers/PYSEC-2024-228.yaml
- https://www.zerodayinitiative.com/advisories/ZDI-24-1514
