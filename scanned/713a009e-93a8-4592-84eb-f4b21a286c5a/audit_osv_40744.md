# [C] Remote Code Execution via Unrestricted File Upload in Responsive FileManager

## Summary
Severity: Critical
Advisory: CVE-2026-5482
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-5482
Type: osv

## Details
Responsive FileManager's allows an unauthenticated attacker to upload files of any type and extension without restriction using dialog.php endpoint, leading to Remote Code Execution. 

This project is unmaintained at the time of CVE assignment. The vulnerability was found in the latest release 9.14.0

## References
- https://cert.pl/en/posts/2026/06/CVE-2026-5482
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5482
- https://github.com/trippo/ResponsiveFilemanager
