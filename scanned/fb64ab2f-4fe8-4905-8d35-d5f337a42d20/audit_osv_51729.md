# [H] CVE-2021-38300

## Summary
Severity: High
Advisory: CVE-2021-38300
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-38300
Type: osv

## Details
arch/mips/net/bpf_jit.c in the Linux kernel before 5.4.10 can generate undesirable machine code when transforming unprivileged cBPF programs, allowing execution of arbitrary code within the kernel context. This occurs because conditional branches can exceed the 128 KB limit of the MIPS architecture.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.10
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20211008-0003/
- https://www.debian.org/security/2022/dsa-5096
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=37cb28ec7d3a36a5bace7063a3dba633ab110f8b
- http://www.openwall.com/lists/oss-security/2021/09/15/5
