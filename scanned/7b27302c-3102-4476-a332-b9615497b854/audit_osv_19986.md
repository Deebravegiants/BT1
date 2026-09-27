# [H] CVE-2021-28906

## Summary
Severity: High
Advisory: CVE-2021-28906
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-28906
Type: osv

## Details
In function read_yin_leaf() in libyang <= v1.0.225, it doesn't check whether the value of retval->ext[r] is NULL. In some cases, it can be NULL, which leads to the operation of retval->ext[r]->flags that results in a crash.

## References
- https://security.gentoo.org/glsa/202107-54
- https://github.com/CESNET/libyang/issues/1455
