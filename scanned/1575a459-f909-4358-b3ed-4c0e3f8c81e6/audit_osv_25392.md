# [C] Chamilo LMS Htaccess File Upload Security Bypass

## Summary
Severity: Critical
Advisory: CVE-2023-3545
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/CVE-2023-3545
Type: osv

## Details
Improper sanitisation in `main/inc/lib/fileUpload.lib.php` in Chamilo LMS <= v1.11.20 on Windows and Apache installations allows unauthenticated attackers to bypass file upload security protections and obtain remote code execution via uploading of `.htaccess` file. This vulnerability may be exploited by privileged attackers or chained with unauthenticated arbitrary file write vulnerabilities, such as CVE-2023-3533, to achieve remote code execution.

## References
- https://github.com/chamilo/chamilo-lms/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3545.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3545
- https://starlabs.sg/advisories/23/23-3545/
- https://support.chamilo.org/projects/chamilo-18/wiki/security_issues#Issue-125-2023-07-13-Critical-impact-Moderate-risk-Htaccess-File-Upload-Security-Bypass-on-Windows-CVE-2023-3545
- https://github.com/chamilo/chamilo-lms/commit/dc7bfce429fbd843a95a57c184b6992c4d709549
