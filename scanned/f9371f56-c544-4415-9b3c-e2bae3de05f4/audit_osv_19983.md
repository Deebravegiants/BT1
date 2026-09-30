# [H] CVE-2021-28903

## Summary
Severity: High
Advisory: CVE-2021-28903
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-28903
Type: osv

## Details
A stack overflow in libyang <= v1.0.225 can cause a denial of service through function lyxml_parse_mem(). lyxml_parse_elem() function will be called recursively, which will consume stack space and lead to crash.

## References
- https://security.gentoo.org/glsa/202107-54
- https://github.com/CESNET/libyang/issues/1453
