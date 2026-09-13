# [H] tcp: add sanity checks to rx zerocopy

## Summary
Severity: High
Advisory: CVE-2024-26640
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-26640
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: add sanity checks to rx zerocopy

TCP rx zerocopy intent is to map pages initially allocated
from NIC drivers, not pages owned by a fs.

This patch adds to can_map_frag() these additional checks:

- Page must not be a compound one.
- page->mapping must be NULL.

This fixes the panic reported by ZhangPeng.

syzbot was able to loopback packets built with sendfile(),
mapping pages owned by an ext4 file to TCP rx zerocopy.

r3 = socket$inet_tcp(0x2, 0x1, 0x0)
mmap(&(0x7f0000ff9000/0x4000)=nil, 0x4000, 0x0, 0x12, r3, 0x0)
r4 = socket$inet_tcp(0x2, 0x1, 0x0)
bind$inet(r4, &(0x7f0000000000)={0x2, 0x4e24, @multicast1}, 0x10)
connect$inet(r4, &(0x7f00000006c0)={0x2, 0x4e24, @empty}, 0x10)
r5 = openat$dir(0xffffffffffffff9c, &(0x7f00000000c0)='./file0\x00',
    0x181e42, 0x0)
fallocate(r5, 0x0, 0x0, 0x85b8)
sendfile(r4, r5, 0x0, 0x8ba0)
getsockopt$inet_tcp_TCP_ZEROCOPY_RECEIVE(r4, 0x6, 0x23,
    &(0x7f00000001c0)={&(0x7f0000ffb000/0x3000)=nil, 0x3000, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0}, &(0x7f0000000440)=0x40)
r6 = openat$dir(0xffffffffffffff9c, &(0x7f00000000c0)='./file0\x00',
    0x181e42, 0x0)

## References
- https://git.kernel.org/stable/c/1b8adcc0e2c584fec778add7777fe28e20781e60
- https://git.kernel.org/stable/c/577e4432f3ac810049cb7e6b71f4d96ec7c6e894
- https://git.kernel.org/stable/c/718f446e60316bf606946f7f42367d691d21541e
- https://git.kernel.org/stable/c/b383d4ea272fe5795877506dcce5aad1f6330e5e
- https://git.kernel.org/stable/c/d15cc0f66884ef2bed28c7ccbb11c102aa3a0760
- https://git.kernel.org/stable/c/f48bf9a83b1666d934247cb58a9887d7b3127b6f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26640.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
