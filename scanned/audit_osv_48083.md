# [H] CVE-2017-17863

## Summary
Severity: High
Advisory: CVE-2017-17863
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17863
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel 4.9.x through 4.9.71 does not check the relationship between pointer values and the BPF stack, which allows local users to cause a denial of service (integer overflow or invalid memory access) or possibly have unspecified other impact.

## References
- https://usn.ubuntu.com/3523-3/
- http://www.securityfocus.com/bid/102321
- http://www.securitytracker.com/id/1040058
- https://usn.ubuntu.com/usn/usn-3523-2/
- https://www.debian.org/security/2017/dsa-4073
- https://www.spinics.net/lists/stable/msg206985.html
- https://anonscm.debian.org/cgit/kernel/linux.git/tree/debian/patches/bugfix/all/bpf-reject-out-of-bounds-stack-pointer-calculation.patch?h=stretch-security
