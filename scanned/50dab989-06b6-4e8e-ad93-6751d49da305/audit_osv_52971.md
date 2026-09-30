# [H] CVE-2022-23222

## Summary
Severity: High
Advisory: CVE-2022-23222
Aliases: A-215814262, PUB-A-215814262
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2022-23222
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 5.15.14 allows local users to gain privileges because of the availability of pointer arithmetic via certain *_OR_NULL pointer types.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z5VTIZZUPC73IEJNZX66BY2YCBRZAELB/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=64620e0a1e712a778095bd35cbb277dc2259281f
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FCR3LIRUEXR7CA63W5M2HT3K63MZGKBR/
- https://www.openwall.com/lists/oss-security/2022/01/13/1
- http://www.openwall.com/lists/oss-security/2022/06/04/3
- http://www.openwall.com/lists/oss-security/2022/06/07/3
- https://security.netapp.com/advisory/ntap-20220217-0002/
- http://www.openwall.com/lists/oss-security/2022/01/14/1
- https://www.debian.org/security/2022/dsa-5050
- https://bugzilla.suse.com/show_bug.cgi?id=1194765
- http://www.openwall.com/lists/oss-security/2022/06/01/1
- http://www.openwall.com/lists/oss-security/2022/01/18/2
