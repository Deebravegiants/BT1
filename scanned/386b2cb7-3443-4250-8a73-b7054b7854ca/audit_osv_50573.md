# [M] CVE-2020-23856

## Summary
Severity: Medium
Advisory: CVE-2020-23856
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/CVE-2020-23856
Type: osv

## Details
Use-after-Free vulnerability in cflow 1.6 in the void call(char *name, int line) function at src/parser.c, which could cause a denial of service via the pointer variable caller->callee.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BLSXGFK2NYPCJMPHSHE3W56ZU3ZO6RD7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZTTKZX274BVFZX7TMPEZG6UWL6UPMQF/
- https://github.com/yangjiageng/PoC/blob/master/PoC_cflow_uaf_parser_line1284
- https://lists.gnu.org/archive/html/bug-cflow/2020-07/msg00000.html
