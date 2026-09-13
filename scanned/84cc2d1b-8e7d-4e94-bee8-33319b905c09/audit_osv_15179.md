# [M] CVE-2019-14295

## Summary
Severity: Medium
Advisory: CVE-2019-14295
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-27
Source: https://osv.dev/vulnerability/CVE-2019-14295
Type: osv

## Details
An Integer overflow in the getElfSections function in p_vmlinx.cpp in UPX 3.95 allows remote attackers to cause a denial of service (crash) via a skewed offset larger than the size of the PE section in a UPX packed executable, which triggers an allocation of excessive memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MOCJ43HTM45GZCAQ2FLEBDNBM76V22RG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T52JATXV6NTPTMGXCRGT37H6KXERYNZN/
- https://github.com/upx/upx/issues/286
