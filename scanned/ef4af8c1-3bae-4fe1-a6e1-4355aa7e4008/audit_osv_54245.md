# [H] CVE-2023-44466

## Summary
Severity: High
Advisory: CVE-2023-44466
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-29
Source: https://osv.dev/vulnerability/CVE-2023-44466
Type: osv

## Details
An issue was discovered in net/ceph/messenger_v2.c in the Linux kernel before 6.4.5. There is an integer signedness error, leading to a buffer overflow and remote code execution via HELLO or one of the AUTH frames. This occurs because of an untrusted length taken from a TCP packet in ceph_decode_32.

## References
- https://security.netapp.com/advisory/ntap-20231116-0003/
- https://github.com/torvalds/linux/commit/a282a2f10539dce2aa619e71e1817570d557fc97
- https://www.spinics.net/lists/ceph-devel/msg57909.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a282a2f10539dce2aa619e71e1817570d557fc97
- https://github.com/google/security-research/security/advisories/GHSA-jg27-jx6w-xwph
