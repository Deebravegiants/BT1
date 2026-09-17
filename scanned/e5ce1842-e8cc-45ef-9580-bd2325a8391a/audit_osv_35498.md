# [C] Foundation Agents MetaGPT actionoutput_str_to_mapping Code Injection Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-0761
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0761
Type: osv

## Details
Foundation Agents MetaGPT actionoutput_str_to_mapping Code Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Foundation Agents MetaGPT. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the actionoutput_str_to_mapping function. The issue results from the lack of proper validation of a user-supplied string before using it to execute Python code. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-28124.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0761.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0761
- https://www.zerodayinitiative.com/advisories/ZDI-26-027/
