# [M] CVE-2020-23930

## Summary
Severity: Medium
Advisory: CVE-2020-23930
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23930
Type: osv

## Details
An issue was discovered in gpac through 20200801. A NULL pointer dereference exists in the function nhmldump_send_header located in write_nhml.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/gpac/gpac/commit/9eeac00b38348c664dfeae2525bba0cf1bc32349
- https://github.com/gpac/gpac/issues/1565
