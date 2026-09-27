# [H] fs/9p: only translate RWX permissions for plain 9P2000

## Summary
Severity: High
Advisory: CVE-2024-36964
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-36964
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/9p: only translate RWX permissions for plain 9P2000

Garbage in plain 9P2000's perm bits is allowed through, which causes it
to be able to set (among others) the suid bit. This was presumably not
the intent since the unix extended bits are handled explicitly and
conditionally on .u.

## References
- https://git.kernel.org/stable/c/157d468e34fdd3cb1ddc07c2be32fb3b02826b02
- https://git.kernel.org/stable/c/5a605930e19f451294bd838754f7d66c976a8a2c
- https://git.kernel.org/stable/c/ad4f65328661392de74e3608bb736fedf3b67e32
- https://git.kernel.org/stable/c/ca9b5c81f0c918c63d73d962ed8a8e231f840bc8
- https://git.kernel.org/stable/c/cd25e15e57e68a6b18dc9323047fe9c68b99290b
- https://git.kernel.org/stable/c/df1962a199783ecd66734d563caf0fedecf08f96
- https://git.kernel.org/stable/c/e55c601af3b1223a84f9f27f9cdbd2af5e203bf3
- https://git.kernel.org/stable/c/e90bc596a74bb905e0a45bf346038c3f9d1e868d
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36964.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36964
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
