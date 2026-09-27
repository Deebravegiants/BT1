# [M] CVE-2021-32276

## Summary
Severity: Medium
Advisory: CVE-2021-32276
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32276
Type: osv

## Details
An issue was discovered in faad2 through 2.10.0. A NULL pointer dereference exists in the function get_sample() located in output.c. It allows an attacker to cause Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00020.html
- https://www.debian.org/security/2022/dsa-5109
- https://github.com/knik0/faad2/issues/58
