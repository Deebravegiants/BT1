# [H] CVE-2020-28025

## Summary
Severity: High
Advisory: CVE-2020-28025
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28025
Type: osv

## Details
Exim 4 before 4.94.2 allows Out-of-bounds Read because pdkim_finish_bodyhash does not validate the relationship between sig->bodyhash.len and b->bh.len; thus, a crafted DKIM-Signature header might lead to a leak of sensitive information from process memory.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28025-BHASH.txt
