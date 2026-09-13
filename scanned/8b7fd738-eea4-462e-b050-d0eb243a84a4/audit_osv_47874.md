# [M] CVE-2017-14140

## Summary
Severity: Medium
Advisory: CVE-2017-14140
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14140
Type: osv

## Details
The move_pages system call in mm/migrate.c in the Linux kernel before 4.12.9 doesn't check the effective uid of the target process, enabling a local attacker to learn the memory layout of a setuid executable despite ASLR.

## References
- http://www.securityfocus.com/bid/100876
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://source.android.com/security/bulletin/pixel/2018-01-01
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.9
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- http://www.debian.org/security/2017/dsa-3981
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=197e7e521384a23b9e585178f3f11c9fa08274b9
- https://github.com/torvalds/linux/commit/197e7e521384a23b9e585178f3f11c9fa08274b9
