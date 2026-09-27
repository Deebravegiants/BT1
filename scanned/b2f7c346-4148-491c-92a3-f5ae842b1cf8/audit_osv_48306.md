# [M] CVE-2017-6009

## Summary
Severity: Medium
Advisory: CVE-2017-6009
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-16
Source: https://osv.dev/vulnerability/CVE-2017-6009
Type: osv

## Details
An issue was discovered in icoutils 0.31.1. A buffer overflow was observed in the "decode_ne_resource_id" function in the "restable.c" source file. This is happening because the "len" parameter for memcpy is not checked for size and thus becomes a negative integer in the process, resulting in a failed memcpy. This affects wrestool.

## References
- https://security.gentoo.org/glsa/201801-12
- http://rhn.redhat.com/errata/RHSA-2017-0837.html
- http://www.debian.org/security/2017/dsa-3807
- http://www.securityfocus.com/bid/96292
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854050
