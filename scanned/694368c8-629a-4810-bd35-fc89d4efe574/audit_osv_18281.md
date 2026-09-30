# [C] CVE-2020-25756

## Summary
Severity: Critical
Advisory: CVE-2020-25756
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-18
Source: https://osv.dev/vulnerability/CVE-2020-25756
Type: osv

## Details
A buffer overflow vulnerability exists in the mg_get_http_header function in Cesanta Mongoose 6.18 due to a lack of bounds checking. A crafted HTTP header can exploit this bug. NOTE: a committer has stated "this will not happen in practice.

## References
- https://github.com/cesanta/mongoose/issues/1135
