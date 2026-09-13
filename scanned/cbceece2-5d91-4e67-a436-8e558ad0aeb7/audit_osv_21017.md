# [H] CVE-2021-39534

## Summary
Severity: High
Advisory: CVE-2021-39534
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-39534
Type: osv

## Details
An issue was discovered in libslax through v0.22.1. slaxIsCommentStart() in slaxlexer.c has a heap-based buffer overflow.

## References
- https://github.com/Juniper/libslax/issues/52
