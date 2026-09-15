# [C] CVE-2018-20062

## Summary
Severity: Critical
Advisory: CVE-2018-20062
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-11
Source: https://osv.dev/vulnerability/CVE-2018-20062
Type: osv

## Details
An issue was discovered in NoneCms V1.3. thinkphp/library/think/App.php allows remote attackers to execute arbitrary PHP code via crafted use of the filter parameter, as demonstrated by the s=index/\think\Request/input&filter=phpinfo&data=1 query string.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-20062
- http://packetstormsecurity.com/files/157218/ThinkPHP-5.0.23-Remote-Code-Execution.html
- https://github.com/nangge/noneCms/issues/21
