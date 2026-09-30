# [H] Hugging Face Transformers SEW convert_config Code Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-14926
Aliases: PYSEC-2025-214
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-14926
Type: osv

## Details
Hugging Face Transformers SEW convert_config Code Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Hugging Face Transformers. User interaction is required to exploit this vulnerability in that the target must convert a malicious checkpoint.

The specific flaw exists within the convert_config function. The issue results from the lack of proper validation of a user-supplied string before using it to execute Python code. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-28251.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14926.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14926
- https://www.zerodayinitiative.com/advisories/ZDI-25-1147/
