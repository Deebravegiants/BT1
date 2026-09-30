# [H] CVE-2025-12121

## Summary
Severity: High
Advisory: CVE-2025-12121
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-12121
Type: osv

## Details
Lite XL versions 2.1.8 and prior contain a vulnerability in the system.exec function, which allowed arbitrary command execution through unsanitized shell command construction. This function was used in project directory launching (core.lua), drag-and-drop file handling (rootview.lua), and the “open in system” command in the treeview plugin (treeview.lua). If an attacker could influence input to system.exec, they might execute arbitrary commands with the privileges of the Lite XL process.

## References
- https://kb.cert.org/vuls/id/579478
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12121.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12121
- https://github.com/lite-xl/lite-xl/pull/2163
