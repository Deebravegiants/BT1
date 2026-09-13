# [H] CVE-2016-10248

## Summary
Severity: High
Advisory: CVE-2016-10248
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10248
Type: osv

## Details
The jpc_tsfb_synthesize function in jpc_tsfb.c in JasPer before 1.900.9 allows remote attackers to cause a denial of service (NULL pointer dereference) via vectors involving an empty sequence.

## References
- http://www.securityfocus.com/bid/93797
- https://usn.ubuntu.com/3693-1/
- https://access.redhat.com/errata/RHSA-2017:1208
- https://blogs.gentoo.org/ago/2016/10/20/jasper-null-pointer-dereference-in-jpc_tsfb_synthesize-jpc_tsfb-c/
- https://github.com/mdadams/jasper/commit/2e82fa00466ae525339754bb3ab0a0474a31d4bd
