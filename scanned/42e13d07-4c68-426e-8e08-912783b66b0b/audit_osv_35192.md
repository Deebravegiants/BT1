# [C] Frappe may be vulnerable remote code execution due to server-side template injection

## Summary
Severity: Critical
Advisory: CVE-2025-68929
Aliases: GHSA-qq98-vfv9-xmxh
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-68929
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 14.99.6 and 15.88.1, an authenticated user with specific permissions could be tricked into accessing a specially crafted link. This could lead to a malicious template being executed on the server, resulting in remote code execution. Versions 14.99.6 and 15.88.1 fix the issue. No known workarounds are available.

## References
- https://github.com/frappe/frappe/releases/tag/v14.99.6
- https://github.com/frappe/frappe/releases/tag/v15.88.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68929.json
- https://github.com/frappe/frappe/security/advisories/GHSA-qq98-vfv9-xmxh
- https://nvd.nist.gov/vuln/detail/CVE-2025-68929
