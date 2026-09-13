# [H] CVE-2017-17712

## Summary
Severity: High
Advisory: CVE-2017-17712
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-16
Source: https://osv.dev/vulnerability/CVE-2017-17712
Type: osv

## Details
The raw_sendmsg() function in net/ipv4/raw.c in the Linux kernel through 4.14.6 has a race condition in inet->hdrincl that leads to uninitialized stack pointer usage; this allows a local user to execute code and gain privileges.

## References
- https://usn.ubuntu.com/3581-1/
- https://usn.ubuntu.com/3581-3/
- https://usn.ubuntu.com/3582-2/
- https://access.redhat.com/errata/RHSA-2018:0502
- https://source.android.com/security/bulletin/pixel/2018-04-01
- https://usn.ubuntu.com/3581-2/
- https://usn.ubuntu.com/3582-1/
- https://www.debian.org/security/2017/dsa-4073
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8f659a03a0ba9289b9aeb9b4470e6fb263d6f483
- https://github.com/torvalds/linux/commit/8f659a03a0ba9289b9aeb9b4470e6fb263d6f483
