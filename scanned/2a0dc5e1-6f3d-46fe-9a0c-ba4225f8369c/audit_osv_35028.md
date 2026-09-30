# [H] CVE-2025-67738

## Summary
Severity: High
Advisory: CVE-2025-67738
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-67738
Type: osv

## Details
squid/cachemgr.cgi in Webmin before 2.600 does not properly quote arguments. This is relevant if Webmin's Squid module and its Cache Manager feature are available, and an untrusted party is able to authenticate to Webmin and has certain Cache Manager permissions (the "cms" security option).

## References
- https://github.com/webmin/webmin/compare/2.520...2.600
- https://webmin.com/security/#privilige-escalation-using-squid-module-cve-2025-67738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67738.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67738
- https://github.com/webmin/webmin/commit/1a52bf4d72f9da6d79250c66e51f41c6f5b880ee
