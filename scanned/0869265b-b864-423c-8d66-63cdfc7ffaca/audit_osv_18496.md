# [H] CVE-2020-28009

## Summary
Severity: High
Advisory: CVE-2020-28009
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28009
Type: osv

## Details
Exim 4 before 4.94.2 allows Integer Overflow to Buffer Overflow because get_stdinput allows unbounded reads that are accompanied by unbounded increases in a certain size variable. NOTE: exploitation may be impractical because of the execution time needed to overflow (multiple days).

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28009-STDIN.txt
