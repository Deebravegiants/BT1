# [C] CVE-2019-13086

## Summary
Severity: Critical
Advisory: CVE-2019-13086
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13086
Type: osv

## Details
core/MY_Security.php in CSZ CMS 1.2.2 before 2019-06-20 has member/login/check SQL injection by sending a crafted HTTP User-Agent header and omitting the csrf_csz parameter.

## References
- https://github.com/cskaza/cszcms/issues/19
