# [H] erofs: fix crafted invalid cases for encoded extents

## Summary
Severity: High
Advisory: CVE-2025-40241
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40241
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix crafted invalid cases for encoded extents

Robert recently reported two corrupted images that can cause system
crashes, which are related to the new encoded extents introduced
in Linux 6.15:

  - The first one [1] has plen != 0 (e.g. plen == 0x2000000) but
    (plen & Z_EROFS_EXTENT_PLEN_MASK) == 0. It is used to represent
    special extents such as sparse extents (!EROFS_MAP_MAPPED), but
    previously only plen == 0 was handled;

  - The second one [2] has pa 0xffffffffffdcffed and plen 0xb4000,
    then "cur [0xfffffffffffff000] += bvec.bv_len [0x1000]" in
    "} while ((cur += bvec.bv_len) < end);" wraps around, causing an
    out-of-bound access of pcl->compressed_bvecs[] in
    z_erofs_submit_queue().  EROFS only supports 48-bit physical block
    addresses (up to 1EiB for 4k blocks), so add a sanity check to
    enforce this.

## References
- https://git.kernel.org/stable/c/00d8fe0b72f4ca0a983abced36aad2160038c421
- https://git.kernel.org/stable/c/a429b76114aaca3ef1aff4cd469dcf025431bd11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40241.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
