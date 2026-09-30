# [H] CVE-2017-2584

## Summary
Severity: High
Advisory: CVE-2017-2584
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-01-15
Source: https://osv.dev/vulnerability/CVE-2017-2584
Type: osv

## Details
arch/x86/kvm/emulate.c in the Linux kernel through 4.9.3 allows local users to obtain sensitive information from kernel memory or cause a denial of service (use-after-free) via a crafted application that leverages instruction emulation for fxrstor, fxsave, sgdt, and sidt.

## References
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=129a72a0d3c8e139a04512325384fe5ac119e74d
- http://www.openwall.com/lists/oss-security/2017/01/13/7
- http://www.securityfocus.com/bid/95430
- http://www.securitytracker.com/id/1037603
- http://www.debian.org/security/2017/dsa-3791
- https://bugzilla.redhat.com/show_bug.cgi?id=1413001
- https://github.com/torvalds/linux/commit/129a72a0d3c8e139a04512325384fe5ac119e74d
