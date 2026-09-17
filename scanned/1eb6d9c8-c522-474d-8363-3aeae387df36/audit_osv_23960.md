# [H] gfs2: Always check inode size of inline inodes

## Summary
Severity: High
Advisory: CVE-2022-49739
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49739
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.19.280, >=4.20.0 <5.4.240, >=5.5.0 <5.10.177, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Always check inode size of inline inodes

Check if the inode size of stuffed (inline) inodes is within the allowed
range when reading inodes from disk (gfs2_dinode_in()).  This prevents
us from on-disk corruption.

The two checks in stuffed_readpage() and gfs2_unstuffer_page() that just
truncate inline data to the maximum allowed size don't actually make
sense, and they can be removed now as well.

## References
- https://git.kernel.org/stable/c/45df749f827c286adbc951f2a4865b67f0442ba9
- https://git.kernel.org/stable/c/46c9088cabd4d0469fdb61ac2a9c5003057fe94d
- https://git.kernel.org/stable/c/4d4cb76636134bf9a0c9c3432dae936f99954586
- https://git.kernel.org/stable/c/70376c7ff31221f1d21db5611d8209e677781d3a
- https://git.kernel.org/stable/c/7c414f6f06e9a3934901b6edc3177ae5a1e07094
- https://git.kernel.org/stable/c/d458a0984429c2d47e60254f5bc4119cbafe83a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49739.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
