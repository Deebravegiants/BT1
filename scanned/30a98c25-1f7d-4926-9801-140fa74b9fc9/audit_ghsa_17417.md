# [C] Hugging Face smolagents: Unsafe deserialization in Remote Python Executor leads to RCE

## Summary
Severity: Critical
Advisory: GHSA-q9r5-6hrr-9ph7
CVE: CVE-2025-14931
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-23
Source: https://github.com/advisories/GHSA-q9r5-6hrr-9ph7
Type: github-advisory

## Affected
- PyPI: `smolagents` — affected >=0

## Details
Hugging Face smolagents Remote Python Executor Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Hugging Face smolagents. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the parsing of pickle data. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-28312.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14931
- https://github.com/huggingface/smolagents
- https://www.zerodayinitiative.com/advisories/ZDI-25-1143
