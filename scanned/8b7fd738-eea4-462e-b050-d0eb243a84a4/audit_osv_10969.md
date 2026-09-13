# [M] CVE-2017-5503

## Summary
Severity: Medium
Advisory: CVE-2017-5503
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5503
Type: osv

## Details
The dec_clnpass function in libjasper/jpc/jpc_t1dec.c in JasPer 1.900.27 allows remote attackers to cause a denial of service (invalid memory write and crash) or possibly have unspecified other impact via a crafted image.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00082.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00085.html
- http://www.securityfocus.com/bid/95683
- https://security.gentoo.org/glsa/201908-03
- http://www.openwall.com/lists/oss-security/2017/01/17/10
- http://www.openwall.com/lists/oss-security/2017/01/16/3
- https://blogs.gentoo.org/ago/2017/01/16/jasper-invalid-memory-write-in-dec_clnpass-jpc_t1dec-c/
