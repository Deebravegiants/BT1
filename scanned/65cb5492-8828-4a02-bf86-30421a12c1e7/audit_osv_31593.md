# [H] FontForge SFD File Parsing Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-15276
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-15276
Type: osv

## Details
FontForge SFD File Parsing Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of FontForge. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of SFD files. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28198.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15276.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15276
- https://www.zerodayinitiative.com/advisories/ZDI-25-1187/
