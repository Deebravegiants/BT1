# [M] CVE-2020-14385

## Summary
Severity: Medium
Advisory: CVE-2020-14385
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14385
Type: osv

## Details
A flaw was found in the Linux kernel before 5.9-rc4. A failure of the file system metadata validator in XFS can cause an inode with a valid, user-creatable extended attribute to be flagged as corrupt. This can lead to the filesystem being shutdown, or otherwise rendered inaccessible until it is remounted, leading to a denial of service. The highest threat from this vulnerability is to system availability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://usn.ubuntu.com/4576-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14385
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f4020438fab05364018c91f7e02ebdd192085933
