# [H] jfs: fix out-of-bounds in dbNextAG() and diAlloc()

## Summary
Severity: High
Advisory: CVE-2024-47723
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47723
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix out-of-bounds in dbNextAG() and diAlloc()

In dbNextAG() , there is no check for the case where bmp->db_numag is
greater or same than MAXAG due to a polluted image, which causes an
out-of-bounds. Therefore, a bounds check should be added in dbMount().

And in dbNextAG(), a check for the case where agpref is greater than
bmp->db_numag should be added, so an out-of-bounds exception should be
prevented.

Additionally, a check for the case where agno is greater or same than
MAXAG should be added in diAlloc() to prevent out-of-bounds.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/0338e66cba272351ca9d7d03f3628e390e70963b
- https://git.kernel.org/stable/c/128d5cfdcf844cb690c9295a3a1c1114c21fc15a
- https://git.kernel.org/stable/c/5ad6284c8d433f8a213111c5c44ead4d9705b622
- https://git.kernel.org/stable/c/6ce8b6ab44a8b5918c0ee373d4ad19d19017931b
- https://git.kernel.org/stable/c/96855f40e152989c9e7c20c4691ace5581098acc
- https://git.kernel.org/stable/c/c1ba4b8ca799ff1d99d01f37d7ccb7d5ba5533d2
- https://git.kernel.org/stable/c/d1017d2a0f3f16dc1db5120e7ddbe7c6680425b0
- https://git.kernel.org/stable/c/e63866a475562810500ea7f784099bfe341e761a
- https://git.kernel.org/stable/c/ead82533278502428883085a787d5a00f15e5eb9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47723.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
