# [M] CVE-2020-27170

## Summary
Severity: Medium
Advisory: CVE-2020-27170
Aliases: A-183840542, PUB-A-183840542
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-20
Source: https://osv.dev/vulnerability/CVE-2020-27170
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.8. kernel/bpf/verifier.c performs undesirable out-of-bounds speculation on pointer arithmetic, leading to side-channel attacks that defeat Spectre mitigations and obtain sensitive information from kernel memory, aka CID-f232326f6966. This affects pointer types that do not define a ptr_limit.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QRTPQE73ANG7D6M4L4PK5ZQDPO4Y2FVD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FB6LUXPEIRLZH32YXWZVEZAD4ZL6SDK2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- http://www.openwall.com/lists/oss-security/2021/03/24/4
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.8
- https://www.openwall.com/lists/oss-security/2021/03/19/2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f232326f6966cf2a1d1db7bc917a4ce5f9f55f76
