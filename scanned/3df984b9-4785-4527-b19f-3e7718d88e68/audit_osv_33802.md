# [H] CVE-2025-50286

## Summary
Severity: High
Advisory: CVE-2025-50286
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-06
Source: https://osv.dev/vulnerability/CVE-2025-50286
Type: osv

## Details
A Remote Code Execution (RCE) vulnerability in Grav CMS v1.7.48 allows an authenticated admin to upload a malicious plugin via the /admin/tools/direct-install interface. Once uploaded, the plugin is automatically extracted and loaded, allowing arbitrary PHP code execution and reverse shell access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50286.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50286
- https://github.com/binneko/CVE-2025-50286
