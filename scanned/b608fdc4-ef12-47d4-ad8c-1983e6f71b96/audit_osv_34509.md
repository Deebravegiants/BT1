# [M] CVE-2025-61189

## Summary
Severity: Medium
Advisory: CVE-2025-61189
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-61189
Type: osv

## Details
Jeecgboot versions 3.8.2 and earlier are affected by a path traversal vulnerability. The endpoint is /sys/comment/addFile. This vulnerability allows attackers to upload files with system-whitelisted extensions to the system directory /opt, instead of the /opt/upFiles directory specified by the web server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61189.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61189
- https://github.com/jeecgboot/JeecgBoot/issues/8827
