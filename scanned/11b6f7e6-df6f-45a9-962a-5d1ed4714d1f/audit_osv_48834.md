# [M] CVE-2018-15470

## Summary
Severity: Medium
Advisory: CVE-2018-15470
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/CVE-2018-15470
Type: osv

## Details
An issue was discovered in Xen through 4.11.x. The logic in oxenstored for handling writes depended on the order of evaluation of expressions making up a tuple. As indicated in section 7.7.3 "Operations on data structures" of the OCaml manual, the order of evaluation of subexpressions is not specified. In practice, different implementations behave differently. Thus, oxenstored may not enforce the configured quota-maxentity. This allows a malicious or buggy guest to write as many xenstore entries as it wishes, causing unbounded memory usage in oxenstored. This can lead to a system-wide DoS.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- http://xenbits.xen.org/xsa/advisory-272.html
- https://security.gentoo.org/glsa/201810-06
