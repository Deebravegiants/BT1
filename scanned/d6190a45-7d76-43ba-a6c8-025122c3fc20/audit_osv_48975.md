# [M] CVE-2018-19407

## Summary
Severity: Medium
Advisory: CVE-2018-19407
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-21
Source: https://osv.dev/vulnerability/CVE-2018-19407
Type: osv

## Details
The vcpu_scan_ioapic function in arch/x86/kvm/x86.c in the Linux kernel through 4.19.2 allows local users to cause a denial of service (NULL pointer dereference and BUG) via crafted system calls that reach a situation where ioapic is uninitialized.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3872-1/
- https://usn.ubuntu.com/3878-2/
- https://usn.ubuntu.com/3879-1/
- https://usn.ubuntu.com/3879-2/
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3878-1/
- http://www.securityfocus.com/bid/105987
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-4/
- https://lkml.org/lkml/2018/11/20/580
