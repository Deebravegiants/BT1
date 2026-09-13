# [H] jfs: check if leafidx greater than num leaves per dmap tree

## Summary
Severity: High
Advisory: CVE-2024-49902
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49902
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: check if leafidx greater than num leaves per dmap tree

syzbot report a out of bounds in dbSplit, it because dmt_leafidx greater
than num leaves per dmap tree, add a checking for dmt_leafidx in dbFindLeaf.

Shaggy:
Modified sanity check to apply to control pages as well as leaf pages.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/058aa89b3318be3d66a103ba7c68d717561e1dc6
- https://git.kernel.org/stable/c/2451e5917c56be45d4add786e2a059dd9c2c37c4
- https://git.kernel.org/stable/c/25d2a3ff02f22e215ce53355619df10cc5faa7ab
- https://git.kernel.org/stable/c/35b91f15f44ce3c01eba058ccb864bb04743e792
- https://git.kernel.org/stable/c/4a7bf6a01fb441009a6698179a739957efd88e38
- https://git.kernel.org/stable/c/7fff9a9f866e99931cf6fa260288e55d01626582
- https://git.kernel.org/stable/c/cb0eb10558802764f07de1dc439c4609e27cb4f0
- https://git.kernel.org/stable/c/d64ff0d2306713ff084d4b09f84ed1a8c75ecc32
- https://git.kernel.org/stable/c/d76b9a4c283c7535ae7c7c9b14984e75402951e1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49902.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49902
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
