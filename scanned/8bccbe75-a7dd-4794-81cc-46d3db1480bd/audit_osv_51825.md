# [M] CVE-2021-41458

## Summary
Severity: Medium
Advisory: CVE-2021-41458
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-16
Source: https://osv.dev/vulnerability/CVE-2021-41458
Type: osv

## Details
In GPAC MP4Box v1.1.0, there is a stack buffer overflow at src/utils/error.c:1769 which leads to a denial of service vulnerability.

## References
- https://github.com/gpac/gpac/issues/1910
