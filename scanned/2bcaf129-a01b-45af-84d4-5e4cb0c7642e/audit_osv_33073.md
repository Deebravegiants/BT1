# [H] fs/ntfs3: Add sanity check for file name

## Summary
Severity: High
Advisory: CVE-2025-38707
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38707
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Add sanity check for file name

The length of the file name should be smaller than the directory entry size.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/27ee9a42b245efe6529e28b03453291a775cb3e4
- https://git.kernel.org/stable/c/2ac47f738ddfc1957a33be163bc97ee8f78e85a6
- https://git.kernel.org/stable/c/3572737a768dadea904ebc4eb34b6ed575bb72d9
- https://git.kernel.org/stable/c/b51642fc52d1c7243a9361555d5c4b24d7569d7e
- https://git.kernel.org/stable/c/bde58c1539f3ffddffc94d64007de16964e6b8eb
- https://git.kernel.org/stable/c/e841ecb139339602bc1853f5f09daa5d1ea920a2
- https://git.kernel.org/stable/c/f99eb9a641f4ef927d8724f4966dcfd1f0e9f835
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38707.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
