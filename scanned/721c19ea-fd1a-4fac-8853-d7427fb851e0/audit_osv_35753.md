# [C] Path Traversal: '.../...//' in Crafty Controller

## Summary
Severity: Critical
Advisory: CVE-2026-13716
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-13716
Type: osv

## Details
Path traversal in server import and admin file upload in Crafty Controller. Allows a remote, authenticated attacker to upload files to arbitrary paths permitted to the Crafty Controller application and perform remote code execution.

## References
- https://gitlab.com/crafty-controller/crafty-4/-/work_items/727
- https://gitlab.com/crafty-controller/crafty-4/-/work_items/740
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13716.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13716
