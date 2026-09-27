# [M] CVE-2017-17741

## Summary
Severity: Medium
Advisory: CVE-2017-17741
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-12-18
Source: https://osv.dev/vulnerability/CVE-2017-17741
Type: osv

## Details
The KVM implementation in the Linux kernel through 4.14.7 allows attackers to obtain potentially sensitive information from kernel memory, aka a write_mmio stack-based out-of-bounds read, related to arch/x86/kvm/x86.c and include/trace/events/kvm.h.

## References
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3620-1/
- https://usn.ubuntu.com/3620-2/
- http://www.securityfocus.com/bid/102227
- https://lists.debian.org/debian-lts-announce/2018/01/msg00004.html
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3632-1/
- https://www.debian.org/security/2018/dsa-4082
- https://www.debian.org/security/2017/dsa-4073
- https://www.spinics.net/lists/kvm/msg160796.html
