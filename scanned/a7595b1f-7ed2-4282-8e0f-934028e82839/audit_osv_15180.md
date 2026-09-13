# [H] CVE-2019-14296

## Summary
Severity: High
Advisory: CVE-2019-14296
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-27
Source: https://osv.dev/vulnerability/CVE-2019-14296
Type: osv

## Details
canUnpack in p_vmlinx.cpp in UPX 3.95 allows remote attackers to cause a denial of service (SEGV or buffer overflow, and application crash) or possibly have unspecified other impact via a crafted UPX packed file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MOCJ43HTM45GZCAQ2FLEBDNBM76V22RG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T52JATXV6NTPTMGXCRGT37H6KXERYNZN/
- https://github.com/upx/upx/issues/287
