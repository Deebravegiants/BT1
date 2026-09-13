# [H] CVE-2021-32278

## Summary
Severity: High
Advisory: CVE-2021-32278
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32278
Type: osv

## Details
An issue was discovered in faad2 through 2.10.0. A heap-buffer-overflow exists in the function lt_prediction located in lt_predict.c. It allows an attacker to cause code Execution.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00020.html
- https://www.debian.org/security/2022/dsa-5109
- https://github.com/knik0/faad2/issues/62
