# [H] NFS/localio: Fix a race in nfs_local_open_fh()

## Summary
Severity: High
Advisory: CVE-2025-38028
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38028
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS/localio: Fix a race in nfs_local_open_fh()

Once the clp->cl_uuid.lock has been dropped, another CPU could come in
and free the struct nfsd_file that was just added. To prevent that from
happening, take the RCU read lock before dropping the spin lock.

## References
- https://git.kernel.org/stable/c/185a2f2ddabdcf999823f61de67f86376883920d
- https://git.kernel.org/stable/c/fa7ab64f1e2fdc8f2603aab8e0dd20de89cb10d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38028.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
