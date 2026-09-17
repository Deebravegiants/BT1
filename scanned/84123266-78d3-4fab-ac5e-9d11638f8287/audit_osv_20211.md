# [H] CVE-2021-32272

## Summary
Severity: High
Advisory: CVE-2021-32272
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32272
Type: osv

## Details
An issue was discovered in faad2 before 2.10.0. A heap-buffer-overflow exists in the function stszin located in mp4read.c. It allows an attacker to cause Code Execution.

## References
- https://www.debian.org/security/2022/dsa-5109
- https://github.com/knik0/faad2/issues/57
- https://github.com/knik0/faad2/commit/1b71a6ba963d131375f5e489b3b25e36f19f3f24
