# [M] CVE-2020-25641

## Summary
Severity: Medium
Advisory: CVE-2020-25641
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-25641
Type: osv

## Details
A flaw was found in the Linux kernel's implementation of biovecs in versions before 5.9-rc7. A zero-length biovec request issued by the block subsystem could cause the kernel to enter an infinite loop, causing a denial of service. This flaw allows a local attacker with basic privileges to issue requests to a block device, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://usn.ubuntu.com/4576-1/
- https://www.kernel.org/doc/html/latest/block/biovecs.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00042.html
- http://www.openwall.com/lists/oss-security/2020/10/06/9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7e24969022cbd61ddc586f14824fc205661bb124
- https://bugzilla.redhat.com/show_bug.cgi?id=1881424
