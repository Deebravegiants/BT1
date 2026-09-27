# [M] CVE-2020-14314

## Summary
Severity: Medium
Advisory: CVE-2020-14314
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14314
Type: osv

## Details
A memory out-of-bounds read flaw was found in the Linux kernel before 5.9-rc2 with the ext3/ext4 file system, in the way it accesses a directory with broken indexing. This flaw allows a local user to crash the system if the directory exists. The highest threat from this vulnerability is to system availability.

## References
- https://lore.kernel.org/linux-ext4/f53e246b-647c-64bb-16ec-135383c70ad7%40redhat.com/T/#u
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://usn.ubuntu.com/4576-1/
- https://usn.ubuntu.com/4578-1/
- https://www.starwindsoftware.com/security/sw-20210325-0003/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://usn.ubuntu.com/4579-1/
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14314
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5872331b3d91820e14716632ebb56b1399b34fe1
