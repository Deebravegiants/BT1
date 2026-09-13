# [C] nfsd: fix refcount leak in nfsd_set_fh_dentry()

## Summary
Severity: Critical
Advisory: CVE-2025-40212
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-40212
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix refcount leak in nfsd_set_fh_dentry()

nfsd exports a "pseudo root filesystem" which is used by NFSv4 to find
the various exported filesystems using LOOKUP requests from a known root
filehandle.  NFSv3 uses the MOUNT protocol to find those exported
filesystems and so is not given access to the pseudo root filesystem.

If a v3 (or v2) client uses a filehandle from that filesystem,
nfsd_set_fh_dentry() will report an error, but still stores the export
in "struct svc_fh" even though it also drops the reference (exp_put()).
This means that when fh_put() is called an extra reference will be dropped
which can lead to use-after-free and possible denial of service.

Normal NFS usage will not provide a pseudo-root filehandle to a v3
client.  This bug can only be triggered by the client synthesising an
incorrect filehandle.

To fix this we move the assignments to the svc_fh later, after all
possible error cases have been detected.

## References
- https://git.kernel.org/stable/c/8a7348a9ed70bda1c1f51d3f1815bcbdf9f3b38c
- https://git.kernel.org/stable/c/b6bc86ce3944b10b9fc181fc00c1a520a20ed965
- https://git.kernel.org/stable/c/c83d7365cec5eb5ebeeee2a72e29b4ca58a7e4c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40212.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
