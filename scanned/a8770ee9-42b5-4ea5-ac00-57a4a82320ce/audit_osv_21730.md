# [H] CVE-2021-45960

## Summary
Severity: High
Advisory: CVE-2021-45960
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45960
Type: osv

## Details
In Expat (aka libexpat) before 2.4.3, a left shift by 29 (or more) places in the storeAtts function in xmlparse.c can lead to realloc misbehavior (e.g., allocating too few bytes, or only freeing memory).

## References
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220121-0004/
- https://www.tenable.com/security/tns-2022-05
- https://bugzilla.mozilla.org/show_bug.cgi?id=1217609
- https://www.debian.org/security/2022/dsa-5073
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://github.com/libexpat/libexpat/issues/531
- https://github.com/libexpat/libexpat/pull/534
- http://www.openwall.com/lists/oss-security/2022/01/17/3
