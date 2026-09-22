# [M] CVE-2020-26029

## Summary
Severity: Medium
Advisory: CVE-2020-26029
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-26029
Type: osv

## Details
An issue was discovered in Zammad before 3.4.1. There are wrong authorization checks for impersonation requests via X-On-Behalf-Of. The authorization checks are performed for the actual user and not the one given in the X-On-Behalf-Of header.

## References
- https://zammad.com/news/security-advisory-zaa-2020-20
