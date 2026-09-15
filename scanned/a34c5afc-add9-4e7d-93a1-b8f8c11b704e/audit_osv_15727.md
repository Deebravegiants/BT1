# [H] CVE-2019-19204

## Summary
Severity: High
Advisory: CVE-2019-19204
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-19204
Type: osv

## Details
An issue was discovered in Oniguruma 6.x before 6.9.4_rc2. In the function fetch_interval_quantifier (formerly known as fetch_range_quantifier) in regparse.c, PFETCH is called without checking PEND. This leads to a heap-based buffer over-read.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NO267PLHGYZSWX3XTRPKYBKD4J3YOU5V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V3MBNW6Z4DOXSCNWGBLQ7OA3OGUJ44WL/
- https://usn.ubuntu.com/4460-1/
- https://github.com/kkos/oniguruma/releases/tag/v6.9.4_rc2
- https://github.com/tarantula-team/CVE-2019-19204
- https://lists.debian.org/debian-lts-announce/2019/12/msg00002.html
- https://github.com/kkos/oniguruma/issues/162
- https://github.com/ManhNDd/CVE-2019-19204
