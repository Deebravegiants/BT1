# [M] CVE-2016-8882

## Summary
Severity: Medium
Advisory: CVE-2016-8882
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-8882
Type: osv

## Details
The jpc_dec_tilefini function in libjasper/jpc/jpc_dec.c in JasPer before 1.900.8 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/95864
- http://www.debian.org/security/2017/dsa-3785
- http://www.openwall.com/lists/oss-security/2016/10/17/1
- http://www.openwall.com/lists/oss-security/2016/10/23/8
- https://github.com/mdadams/jasper/issues/30
