# [M] CVE-2017-18232

## Summary
Severity: Medium
Advisory: CVE-2017-18232
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18232
Type: osv

## Details
The Serial Attached SCSI (SAS) implementation in the Linux kernel through 4.15.9 mishandles a mutex within libsas, which allows local users to cause a denial of service (deadlock) by triggering certain error-handling code.

## References
- https://usn.ubuntu.com/4163-1/
- https://usn.ubuntu.com/4163-2/
- https://www.debian.org/security/2018/dsa-4187
- http://www.securityfocus.com/bid/103423
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0558f33c06bb910e2879e355192227a8e8f0219d
- https://github.com/torvalds/linux/commit/0558f33c06bb910e2879e355192227a8e8f0219d
