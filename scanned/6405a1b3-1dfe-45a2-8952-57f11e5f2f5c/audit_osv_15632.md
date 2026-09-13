# [H] CVE-2019-18211

## Summary
Severity: High
Advisory: CVE-2019-18211
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-18211
Type: osv

## Details
An issue was discovered in Orckestra C1 CMS through 6.6. The EntityTokenSerializer class in Composite.dll is prone to unvalidated deserialization of wrapped BinaryFormatter payloads, leading to arbitrary remote code execution for any low-privilege user.

## References
- https://github.com/Orckestra/C1-CMS-Foundation/commits/dev
