# [H] Tencent PatrickStar merge_checkpoint Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-13706
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-13706
Type: osv

## Details
Tencent PatrickStar merge_checkpoint Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Tencent PatrickStar. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the merge_checkpoint endpoint. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-27182.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13706.json
- https://github.com/Tencent/PatrickStar/commit/2384535503ea98cfe35ad04e20c0cfc7bf58d5d7
- https://nvd.nist.gov/vuln/detail/CVE-2025-13706
- https://www.zerodayinitiative.com/advisories/ZDI-25-1034/
