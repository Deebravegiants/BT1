# [M] CVE-2020-14309

## Summary
Severity: Medium
Advisory: CVE-2020-14309
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-14309
Type: osv

## Details
There's an issue with grub2 in all versions before 2.06 when handling squashfs filesystems containing a symbolic link with name length of UINT32 bytes in size. The name size leads to an arithmetic overflow leading to a zero-size allocation further causing a heap-based buffer overflow with attacker controlled data.

## References
- https://usn.ubuntu.com/4432-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- https://security.gentoo.org/glsa/202104-05
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=1852022
