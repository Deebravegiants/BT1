# [H] Linux Mint Xreader CBT File Parsing Argument Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44452
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-44452
Type: osv

## Details
Linux Mint Xreader CBT File Parsing Argument Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Linux Mint Xreader. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of CBT files. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-22132.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44452.json
- https://github.com/linuxmint/xreader/commit/cd678889ecfe4e84a5cbcf3a0489e15a5e2e3736
- https://nvd.nist.gov/vuln/detail/CVE-2023-44452
- https://www.zerodayinitiative.com/advisories/ZDI-23-1836/
