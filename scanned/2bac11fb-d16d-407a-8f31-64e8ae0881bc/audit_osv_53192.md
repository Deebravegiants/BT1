# [H] CVE-2022-32981

## Summary
Severity: High
Advisory: CVE-2022-32981
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-10
Source: https://osv.dev/vulnerability/CVE-2022-32981
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.18.3 on powerpc 32-bit platforms. There is a buffer overflow in ptrace PEEKUSER and POKEUSER (aka PEEKUSR and POKEUSR) when accessing floating point registers.

## References
- http://www.openwall.com/lists/oss-security/2022/06/14/3
- https://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux.git/commit/?id=8e1278444446fc97778a5e5c99bca1ce0bbc5ec9
