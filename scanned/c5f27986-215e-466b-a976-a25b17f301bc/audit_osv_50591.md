# [H] CVE-2020-25212

## Summary
Severity: High
Advisory: CVE-2020-25212
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-25212
Type: osv

## Details
A TOCTOU mismatch in the NFS client code in the Linux kernel before 5.8.3 could be used by local attackers to corrupt memory or possibly have unspecified other impact because a size check is in fs/nfs/nfs4proc.c instead of fs/nfs/nfs4xdr.c, aka CID-b4487b935452.

## References
- https://usn.ubuntu.com/4578-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00035.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.3
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://twitter.com/grsecurity/status/1303370421958578179
- https://usn.ubuntu.com/4525-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00042.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://usn.ubuntu.com/4527-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4487b93545214a9db8cbf32e86411677b0cca21
