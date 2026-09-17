# [M] CVE-2019-12614

## Summary
Severity: Medium
Advisory: CVE-2019-12614
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-12614
Type: osv

## Details
An issue was discovered in dlpar_parse_cc_property in arch/powerpc/platforms/pseries/dlpar.c in the Linux kernel through 5.1.6. There is an unchecked kstrdup of prop->name, which might allow an attacker to cause a denial of service (NULL pointer dereference and system crash).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MDURACJVGIBIYBSGDZJTRDPX46H5WPZW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBJHGQXA4PQ5EOGCOXEH3KFDNVZ2I4X7/
- https://support.f5.com/csp/article/K54337315?utm_source=f5support&amp%3Butm_medium=RSS
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- http://www.securityfocus.com/bid/108550
- https://seclists.org/bugtraq/2020/Jan/10
- https://usn.ubuntu.com/4095-1/
- http://packetstormsecurity.com/files/154245/Kernel-Live-Patch-Security-Notice-LSN-0054-1.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://usn.ubuntu.com/4093-1/
- https://usn.ubuntu.com/4094-1/
- https://support.f5.com/csp/article/K54337315
- https://usn.ubuntu.com/4095-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- https://security.netapp.com/advisory/ntap-20190710-0002/
- https://lkml.org/lkml/2019/6/3/526
- https://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux.git/commit/?id=efa9ace68e487ddd29c2b4d6dd23242158f1f607
