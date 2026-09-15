# [H] CVE-2018-18950

## Summary
Severity: High
Advisory: CVE-2018-18950
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-05
Source: https://osv.dev/vulnerability/CVE-2018-18950
Type: osv

## Details
KindEditor through 4.1.11 has a path traversal vulnerability in php/upload_json.php. Anyone can browse a file or directory in the kindeditor/attached/ folder via the path parameter without authentication.

## References
- https://github.com/kindsoft/kindeditor/issues/289
