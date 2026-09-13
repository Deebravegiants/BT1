# [H] Mintty Sixel Image Parsing Heap-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-1052
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2025-1052
Type: osv

## Details
Mintty Sixel Image Parsing Heap-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Mintty. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of sixel images. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-23382.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1052.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1052
- https://www.zerodayinitiative.com/advisories/ZDI-25-084/
