# [C] CVE-2025-50428

## Summary
Severity: Critical
Advisory: CVE-2025-50428
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-50428
Type: osv

## Details
In RaspAP raspap-webgui 3.3.2 and earlier, a command injection vulnerability exists in the includes/hostapd.php script. The vulnerability is due to improper sanitizing of user input passed via the interface parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50428.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50428
- https://github.com/RaspAP/raspap-webgui/pull/1833
- https://blog.smarttecs.com/posts/2025-004-cve-2025-50428/
