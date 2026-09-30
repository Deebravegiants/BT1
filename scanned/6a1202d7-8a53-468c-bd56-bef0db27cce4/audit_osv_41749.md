# [C] pNFS: Fix use-after-free in pnfs_update_layout()

## Summary
Severity: Critical
Advisory: CVE-2026-63800
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63800
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.260, >=5.11.0 <6.1.177, >=5.16.0 <6.6.144, >=6.2.0 <6.12.95, >=6.7.0 <6.18.38, >=6.13.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pNFS: Fix use-after-free in pnfs_update_layout()

When hitting the NFS_LAYOUT_RETURN branch in pnfs_update_layout(),
the code calls pnfs_prepare_to_retry_layoutget(lo). If it succeeds,
pnfs_put_layout_hdr(lo) is called before trace_pnfs_update_layout(),
which still references 'lo'. This results in a use-after-free when the
tracepoint accesses lo's fields.

Fix this by moving the tracepoint call before pnfs_put_layout_hdr(lo).

## References
- https://git.kernel.org/stable/c/13e198a90ca4050f4bee8a3f23680389a6563ccc
- https://git.kernel.org/stable/c/1f24b8302c77dcaf79c64c073877a3b9f4dd25d2
- https://git.kernel.org/stable/c/200e7637f4d6a1342987045eea72641524f909dc
- https://git.kernel.org/stable/c/2883ddd7542b4437a2ab4908fe2773f690e20889
- https://git.kernel.org/stable/c/4ad8b9a85dbf57ca532ee9e65ad7e6498bfbbf98
- https://git.kernel.org/stable/c/7e37e9b3e82ade881e1798e2f4fcc54aff7793c1
- https://git.kernel.org/stable/c/9645aaf689aff57427ece3b9fa47d5b5399417f4
- https://git.kernel.org/stable/c/9c0fb5c09ae5bd68dc0038692af8127029cb0385
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63800.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
