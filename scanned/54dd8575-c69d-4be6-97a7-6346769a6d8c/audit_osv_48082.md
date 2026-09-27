# [M] CVE-2017-17862

## Summary
Severity: Medium
Advisory: CVE-2017-17862
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17862
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 ignores unreachable code, even though it would still be processed by JIT compilers. This behavior, also considered an improper branch-pruning logic issue, could possibly be used by local users for denial of service.

## References
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3619-1/
- http://www.securityfocus.com/bid/102325
- http://www.securitytracker.com/id/1040057
- https://www.debian.org/security/2017/dsa-4073
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c131187db2d3fa2f8bf32fdf4e9a4ef805168467
- https://anonscm.debian.org/cgit/kernel/linux.git/tree/debian/patches/bugfix/all/bpf-fix-branch-pruning-logic.patch?h=stretch-security
- https://github.com/torvalds/linux/commit/c131187db2d3fa2f8bf32fdf4e9a4ef805168467
- https://usn.ubuntu.com/usn/usn-3523-2/
- https://www.spinics.net/lists/stable/msg206984.html
