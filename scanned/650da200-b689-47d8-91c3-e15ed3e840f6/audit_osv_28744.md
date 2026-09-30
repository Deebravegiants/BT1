# [H] octeontx2-af: fix the double free in rvu_npc_freemem()

## Summary
Severity: High
Advisory: CVE-2024-36030
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36030
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: fix the double free in rvu_npc_freemem()

Clang static checker(scan-build) warning：
drivers/net/ethernet/marvell/octeontx2/af/rvu_npc.c:line 2184, column 2
Attempt to free released memory.

npc_mcam_rsrcs_deinit() has released 'mcam->counters.bmap'. Deleted this
redundant kfree() to fix this double free problem.

## References
- https://git.kernel.org/stable/c/6e965eba43e9724f3e603d7b7cc83e53b23d155e
- https://git.kernel.org/stable/c/f5aa87a2c0a72132ffc793fb0a5375b2a65d520a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36030.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
