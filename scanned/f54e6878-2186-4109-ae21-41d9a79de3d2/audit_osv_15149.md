# [H] CVE-2019-13980

## Summary
Severity: High
Advisory: CVE-2019-13980
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-13980
Type: osv

## Details
In Directus 7 API through 2.3.0, uploading of PHP files is blocked only when the Apache HTTP Server is used, leading to uploads/_/originals remote code execution with nginx.

## References
- https://github.com/directus/api/issues/979
