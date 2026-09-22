# [H] CVE-2025-12120

## Summary
Severity: High
Advisory: CVE-2025-12120
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-12120
Type: osv

## Details
Lite XL versions 2.1.8 and prior automatically execute the .lite_project.lua file when opening a project directory, without prompting the user for confirmation. The .lite_project.lua file is intended for project-specific configuration but can contain executable Lua logic. This behavior could allow execution of untrusted Lua code if a user opens a malicious project, potentially leading to arbitrary code execution with the privileges of the Lite XL process.

## References
- https://kb.cert.org/vuls/id/579478
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12120.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12120
- https://github.com/lite-xl/lite-xl/pull/2164
