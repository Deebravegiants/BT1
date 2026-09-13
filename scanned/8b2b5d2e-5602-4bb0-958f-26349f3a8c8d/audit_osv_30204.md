# [M] ceph: remove the incorrect Fw reference check when dirtying pages

## Summary
Severity: Medium
Advisory: CVE-2024-50179
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50179
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: remove the incorrect Fw reference check when dirtying pages

When doing the direct-io reads it will also try to mark pages dirty,
but for the read path it won't hold the Fw caps and there is case
will it get the Fw reference.

## References
- https://git.kernel.org/stable/c/11ab19d48ab877430eed0c7d83810970bbcbc4f6
- https://git.kernel.org/stable/c/126b567a2ef65fc38a71d832bf1216c56816f231
- https://git.kernel.org/stable/c/74b302ebad5b43ac17460fa58092d892a3cba6eb
- https://git.kernel.org/stable/c/9d4f619153bab7fa59736462967821d6521a38cb
- https://git.kernel.org/stable/c/c08dfb1b49492c09cf13838c71897493ea3b424e
- https://git.kernel.org/stable/c/c26c5ec832dd9e9dcd0a0a892a485c99889b68f0
- https://git.kernel.org/stable/c/ea98284fc4fb05f276737d2043b02b62be5a8dfb
- https://git.kernel.org/stable/c/f55e003d261baa7c57d51ae5c8ec1f5c26a35c89
- https://git.kernel.org/stable/c/f863bfd0a2c6c99011c62ea71ac04f8e78707da9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50179.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50179
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
