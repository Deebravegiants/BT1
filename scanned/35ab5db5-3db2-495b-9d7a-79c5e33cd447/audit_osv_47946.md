# [M] CVE-2017-15299

## Summary
Severity: Medium
Advisory: CVE-2017-15299
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-14
Source: https://osv.dev/vulnerability/CVE-2017-15299
Type: osv

## Details
The KEYS subsystem in the Linux kernel through 4.13.7 mishandles use of add_key for a key that already exists but is uninstantiated, which allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a crafted system call.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3798-1/
- https://usn.ubuntu.com/3798-2/
- https://www.mail-archive.com/linux-kernel%40vger.kernel.org/msg1499828.html
- https://access.redhat.com/errata/RHSA-2018:0654
- https://bugzilla.redhat.com/show_bug.cgi?id=1498016
- https://marc.info/?t=150654188100001&r=1&w=2
- https://marc.info/?t=150783958600011&r=1&w=2
