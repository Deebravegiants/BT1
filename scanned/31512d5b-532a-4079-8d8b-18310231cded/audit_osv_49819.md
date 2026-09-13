# [M] CVE-2019-19462

## Summary
Severity: Medium
Advisory: CVE-2019-19462
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-30
Source: https://osv.dev/vulnerability/CVE-2019-19462
Type: osv

## Details
relay_open in kernel/relay.c in the Linux kernel through 5.4.1 allows local users to cause a denial of service (such as relay blockage) by triggering a NULL alloc_percpu result.

## References
- https://lore.kernel.org/lkml/20191129013745.7168-1-dja%40axtens.net/
- https://usn.ubuntu.com/4440-1/
- https://www.debian.org/security/2020/dsa-4698
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://usn.ubuntu.com/4439-1/
- https://www.debian.org/security/2020/dsa-4699
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://syzkaller.appspot.com/bug?id=e4265490d26d6c01cd9bc79dc915ef0a1bf15046
- https://usn.ubuntu.com/4425-1/
- https://security.netapp.com/advisory/ntap-20210129-0004/
- https://syzkaller.appspot.com/bug?id=f4d1cb4330bd3ddf4a628332b4285407b2eedd7b
- https://usn.ubuntu.com/4414-1/
- https://syzkaller-ppc64.appspot.com/bug?id=1c09906c83a8ea811a9e318c2a4f8e243becc6f8
- https://syzkaller-ppc64.appspot.com/bug?id=b05b4d005191cc375cdf848c3d4d980308d50531
