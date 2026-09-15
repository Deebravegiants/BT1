# [H] jfs: xattr: fix buffer overflow for invalid xattr

## Summary
Severity: High
Advisory: CVE-2024-40902
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40902
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: xattr: fix buffer overflow for invalid xattr

When an xattr size is not what is expected, it is printed out to the
kernel log in hex format as a form of debugging.  But when that xattr
size is bigger than the expected size, printing it out can cause an
access off the end of the buffer.

Fix this all up by properly restricting the size of the debug hex dump
in the kernel log.

## References
- https://git.kernel.org/stable/c/1e84c9b1838152a87cf453270a5fa75c5037e83a
- https://git.kernel.org/stable/c/33aecc5799c93d3ee02f853cb94e201f9731f123
- https://git.kernel.org/stable/c/4598233d9748fe4db4e13b9f473588aa25e87d69
- https://git.kernel.org/stable/c/480e5bc21f2c42d90c2c16045d64d824dcdd5ec7
- https://git.kernel.org/stable/c/7c55b78818cfb732680c4a72ab270cc2d2ee3d0f
- https://git.kernel.org/stable/c/b537cb2f4c4a1357479716a9c339c0bda03d873f
- https://git.kernel.org/stable/c/f0dedb5c511ed82cbaff4997a8decf2351ba549f
- https://git.kernel.org/stable/c/fc745f6e83cb650f9a5f2c864158e3a5ea76dad0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40902.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40902
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
