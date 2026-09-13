# [H] partitions: mac: fix handling of bogus partition table

## Summary
Severity: High
Advisory: CVE-2025-21772
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21772
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

partitions: mac: fix handling of bogus partition table

Fix several issues in partition probing:

 - The bailout for a bad partoffset must use put_dev_sector(), since the
   preceding read_part_sector() succeeded.
 - If the partition table claims a silly sector size like 0xfff bytes
   (which results in partition table entries straddling sector boundaries),
   bail out instead of accessing out-of-bounds memory.
 - We must not assume that the partition table contains proper NUL
   termination - use strnlen() and strncmp() instead of strlen() and
   strcmp().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/213ba5bd81b7e97ac6e6190b8f3bc6ba76123625
- https://git.kernel.org/stable/c/27a39d006f85e869be68c1d5d2ce05e5d6445bf5
- https://git.kernel.org/stable/c/40a35d14f3c0dc72b689061ec72fc9b193f37d1f
- https://git.kernel.org/stable/c/6578717ebca91678131d2b1f4ba4258e60536e9f
- https://git.kernel.org/stable/c/7fa9706722882f634090bfc9af642bf9ed719e27
- https://git.kernel.org/stable/c/80e648042e512d5a767da251d44132553fe04ae0
- https://git.kernel.org/stable/c/92527100be38ede924768f4277450dfe8a40e16b
- https://git.kernel.org/stable/c/a3e77da9f843e4ab93917d30c314f0283e28c124
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21772.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21772
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
