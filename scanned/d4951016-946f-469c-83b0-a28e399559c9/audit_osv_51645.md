# [H] CVE-2021-37576

## Summary
Severity: High
Advisory: CVE-2021-37576
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-37576
Type: osv

## Details
arch/powerpc/kvm/book3s_rtas.c in the Linux kernel through 5.13.5 on the powerpc platform allows KVM guest OS users to cause host OS memory corruption via rtas_args.nargs, aka CID-f62f3c20647e.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z2YZ2DNURMYYVDT2NYAFDESJC35KCUDS/
- https://lore.kernel.org/linuxppc-dev/87im0x1lqi.fsf%40mpe.ellerman.id.au/T/#u
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDFA7DSQIPM7XPNXJBXFWXHJFVUBCAG6/
- https://security.netapp.com/advisory/ntap-20210917-0005/
- https://www.debian.org/security/2021/dsa-4978
- http://www.openwall.com/lists/oss-security/2021/07/27/2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f62f3c20647ebd5fb6ecb8f0b477b9281c44c10a
