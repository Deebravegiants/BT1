# [C] Unsanitized Input in langgenius/dify

## Summary
Severity: Critical
Advisory: CVE-2025-3466
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-3466
Type: osv

## Details
langgenius/dify versions 1.1.0 to 1.1.2 are vulnerable to unsanitized input in the code node, allowing execution of arbitrary code with full root permissions. The vulnerability arises from the ability to override global functions in JavaScript, such as parseInt, before sandbox security restrictions are imposed. This can lead to unauthorized access to secret keys, internal network servers, and lateral movement within dify.ai. The issue is resolved in version 1.1.3.

## References
- https://huntr.com/bounties/f8dc17a3-5536-4944-a680-24070903cd2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3466.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3466
- https://github.com/langgenius/dify/commit/1be0d26c1feb4bcbbdd2b4ae4eeb25874aadaddb
