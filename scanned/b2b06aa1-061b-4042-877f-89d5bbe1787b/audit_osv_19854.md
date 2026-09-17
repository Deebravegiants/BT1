# [H] CVE-2021-26843

## Summary
Severity: High
Advisory: CVE-2021-26843
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-07
Source: https://osv.dev/vulnerability/CVE-2021-26843
Type: osv

## Details
An issue was discovered in sthttpd through 2.27.1. On systems where the strcpy function is implemented with memcpy, the de_dotdot function may cause a Denial-of-Service (daemon crash) due to overlapping memory ranges being passed to memcpy. This can triggered with an HTTP GET request for a crafted filename. NOTE: this is similar to CVE-2017-10671, but occurs in a different part of the de_dotdot function.

## References
- https://github.com/blueness/sthttpd/issues/14
