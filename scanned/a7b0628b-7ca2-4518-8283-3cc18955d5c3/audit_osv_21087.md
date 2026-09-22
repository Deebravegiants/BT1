# [C] CVE-2021-40540

## Summary
Severity: Critical
Advisory: CVE-2021-40540
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-40540
Type: osv

## Details
ulfius_uri_logger in Ulfius HTTP Framework before 2.7.4 omits con_info initialization and a con_info->request NULL check for certain malformed HTTP requests.

## References
- https://github.com/babelouest/ulfius/commit/c83f564c184a27145e07c274b305cabe943bbfaa
- https://github.com/babelouest/ulfius/compare/v2.7.3...v2.7.4
- http://packetstormsecurity.com/files/164152/Ulfius-Web-Framework-Remote-Memory-Corruption.html
