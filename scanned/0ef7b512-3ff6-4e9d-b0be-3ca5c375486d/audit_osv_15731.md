# [H] CVE-2019-19246

## Summary
Severity: High
Advisory: CVE-2019-19246
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-19246
Type: osv

## Details
Oniguruma through 6.9.3, as used in PHP 7.3.x and other products, has a heap-based buffer over-read in str_lower_case_match in regexec.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NO267PLHGYZSWX3XTRPKYBKD4J3YOU5V/
- https://bugs.php.net/bug.php?id=78559
- https://lists.debian.org/debian-lts-announce/2019/12/msg00002.html
- https://usn.ubuntu.com/4460-1/
- https://github.com/kkos/oniguruma/commit/d3e402928b6eb3327f8f7d59a9edfa622fec557b
