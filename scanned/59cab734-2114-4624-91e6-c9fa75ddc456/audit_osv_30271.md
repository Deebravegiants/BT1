# [H] vsock/virtio: Initialization of the dangling pointer occurring in vsk->trans

## Summary
Severity: High
Advisory: CVE-2024-50264
Aliases: A-378870958, ASB-A-378870958
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50264
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: Initialization of the dangling pointer occurring in vsk->trans

During loopback communication, a dangling pointer can be created in
vsk->trans, potentially leading to a Use-After-Free condition.  This
issue is resolved by initializing vsk->trans to NULL.

## References
- https://a13xp0p0v.github.io/2025/09/02/kernel-hack-drill-and-CVE-2024-50264.html
- https://git.kernel.org/stable/c/2a6a4e69f255b7aed17f93995691ab4f0d3c2203
- https://git.kernel.org/stable/c/44d29897eafd0e1196453d3003a4d5e0b968eeab
- https://git.kernel.org/stable/c/5f092a4271f6dccf88fe0d132475a17b69ef71df
- https://git.kernel.org/stable/c/5f970935d09934222fdef3d0e20c648ea7a963c1
- https://git.kernel.org/stable/c/6ca575374dd9a507cdd16dfa0e78c2e9e20bd05f
- https://git.kernel.org/stable/c/b110196fec44fe966952004bd426967c2a8fd358
- https://git.kernel.org/stable/c/eb1bdcb7dfc30b24495ee4c5533af0ed135cb5f1
- https://git.kernel.org/stable/c/fd8ae346692a56b4437d626c5460c7104980f389
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50264.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
