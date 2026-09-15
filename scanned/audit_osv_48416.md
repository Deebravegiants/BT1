# [H] CVE-2017-7518

## Summary
Severity: High
Advisory: CVE-2017-7518
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-30
Source: https://osv.dev/vulnerability/CVE-2017-7518
Type: osv

## Details
A flaw was found in the Linux kernel before version 4.12 in the way the KVM module processed the trap flag(TF) bit in EFLAGS during emulation of the syscall instruction, which leads to a debug exception(#DB) being raised in the guest stack. A user/process inside a guest could use this flaw to potentially escalate their privileges inside the guest. Linux guests are not affected by this.

## References
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- http://www.securityfocus.com/bid/99263
- http://www.securitytracker.com/id/1038782
- https://access.redhat.com/errata/RHSA-2018:0395
- https://usn.ubuntu.com/3754-1/
- https://www.debian.org/security/2017/dsa-3981
- https://access.redhat.com/errata/RHSA-2018:0412
- https://access.redhat.com/articles/3290921
- https://www.spinics.net/lists/kvm/msg151817.html
- http://www.openwall.com/lists/oss-security/2017/06/23/5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7518
