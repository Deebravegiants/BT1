# [C] CVE-2025-66916

## Summary
Severity: Critical
Advisory: CVE-2025-66916
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2025-66916
Type: osv

## Details
The snailjob component in RuoYi-Vue-Plus versions 5.5.1 and earlier, interface /snail-job/workflow/check-node-expression can execute QLExpress expressions, but it does not filter user input, allowing attackers to use the File class to perform arbitrary file reading and writing.

## References
- https://gist.github.com/Catherines77/e3f06b9c4cc6298579e858088a243c3d
- https://gitee.com/dromara/RuoYi-Vue-Plus
- https://github.com/Catherines77/code-au/blob/main/ruoyi-vue-plus/QLExpress.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66916.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66916
