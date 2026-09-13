# [C] CVE-2024-25400

## Summary
Severity: Critical
Advisory: CVE-2024-25400
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2024-25400
Type: osv

## Details
Subrion CMS 4.2.1 is vulnerable to SQL Injection via ia.core.mysqli.php. NOTE: this is disputed by multiple third parties because it refers to an HTTP request to a PHP file that only contains a class, without any mechanism for accepting external input, and the reportedly vulnerable method is not present in the file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25400.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25400
- https://github.com/intelliants/subrion/issues/910
