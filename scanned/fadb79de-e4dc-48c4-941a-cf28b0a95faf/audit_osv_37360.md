# [H] NFSD: Hold net reference for the lifetime of /proc/fs/nfs/exports fd

## Summary
Severity: High
Advisory: CVE-2026-31403
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31403
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.253, >=5.11.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Hold net reference for the lifetime of /proc/fs/nfs/exports fd

The /proc/fs/nfs/exports proc entry is created at module init
and persists for the module's lifetime. exports_proc_open()
captures the caller's current network namespace and stores
its svc_export_cache in seq->private, but takes no reference
on the namespace. If the namespace is subsequently torn down
(e.g. container destruction after the opener does setns() to a
different namespace), nfsd_net_exit() calls nfsd_export_shutdown()
which frees the cache. Subsequent reads on the still-open fd
dereference the freed cache_detail, walking a freed hash table.

Hold a reference on the struct net for the lifetime of the open
file descriptor. This prevents nfsd_net_exit() from running --
and thus prevents nfsd_export_shutdown() from freeing the cache
-- while any exports fd is open. cache_detail already stores
its net pointer (cd->net, set by cache_create_net()), so
exports_release() can retrieve it without additional per-file
storage.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/6a8d70e2ad6aad2c345a5048edcb8168036f97d6
- https://git.kernel.org/stable/c/76740c28050dc6db2f5550f1325b00a11bbb3255
- https://git.kernel.org/stable/c/c7f406fb341d6747634b8b1fa5461656e5e56076
- https://git.kernel.org/stable/c/d1a19217995df9c7e4118f5a2820c5032fef2945
- https://git.kernel.org/stable/c/db4a9f99b12a7ee1c19d86c83a3b752c7effa6c6
- https://git.kernel.org/stable/c/e3d77f935639e6ae4b381c80464c31df998d61f4
- https://git.kernel.org/stable/c/e7fcf179b82d3a3730fd8615da01b087cc654d0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31403.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
