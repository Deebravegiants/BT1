# [C] CVE-2019-19012

## Summary
Severity: Critical
Advisory: CVE-2019-19012
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-17
Source: https://osv.dev/vulnerability/CVE-2019-19012
Type: osv

## Details
An integer overflow in the search_in_range function in regexec.c in Oniguruma 6.x before 6.9.4_rc2 leads to an out-of-bounds read, in which the offset of this read is under the control of an attacker. (This only affects the 32-bit compiled version). Remote attackers can cause a denial-of-service or information disclosure, or possibly have unspecified other impact, via a crafted regular expression.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NO267PLHGYZSWX3XTRPKYBKD4J3YOU5V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V3MBNW6Z4DOXSCNWGBLQ7OA3OGUJ44WL/
- https://usn.ubuntu.com/4460-1/
- https://github.com/kkos/oniguruma/releases/tag/v6.9.4_rc2
- https://lists.debian.org/debian-lts-announce/2019/12/msg00002.html
- https://github.com/kkos/oniguruma/issues/164
- https://github.com/tarantula-team/CVE-2019-19012
