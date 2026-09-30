# [H] FontForge GUtils XBM File Parsing Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-15278
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-15278
Type: osv

## Details
FontForge GUtils XBM File Parsing Integer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of FontForge. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of pixels within XBM files. The issue results from the lack of proper validation of user-supplied data, which can result in an integer overflow before allocating a buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-27865.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15278.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15278
- https://www.zerodayinitiative.com/advisories/ZDI-25-1185/
