# [C] ImpressCMS 1.4.4 - Unrestricted File Upload

## Summary
Severity: Critical
Advisory: CVE-2022-50912
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2022-50912
Type: osv

## Details
ImpressCMS 1.4.4 contains a file upload vulnerability with weak extension sanitization that allows attackers to upload potentially malicious files. Attackers can bypass file upload restrictions by using alternative file extensions .php2.php6.php7.phps.pht to execute arbitrary PHP code on the server.

## References
- https://www.impresscms.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50912.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50912
- https://www.vulncheck.com/advisories/impresscms-unrestricted-file-upload
- https://github.com/ImpressCMS/impresscms
- https://www.exploit-db.com/exploits/50890
