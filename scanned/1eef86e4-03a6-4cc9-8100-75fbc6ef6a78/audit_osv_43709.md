# [C] smb: client: Fix use-after-free in cifs_try_adding_channels()

## Summary
Severity: Critical
Advisory: CVE-2026-74608
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74608
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.8.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: Fix use-after-free in cifs_try_adding_channels()

cifs_try_adding_channels() takes a temporary reference to an interface
before dropping iface_lock. If cifs_ses_add_channel() fails, it drops
that reference and then increments iface->weight_fulfilled.

A concurrent interface list refresh can remove the list reference while
channel creation is in progress. In that case, the failure-path
kref_put() releases the last reference and frees iface. Updating
weight_fulfilled afterward then accesses freed memory.

Increment weight_fulfilled before dropping the temporary reference,
keeping iface alive for the final access.

## References
- https://git.kernel.org/stable/c/1305eadc6a7d78a8d0a52eee29ddd2d9e8a27805
- https://git.kernel.org/stable/c/1ffacbadc14530e55b8d86f7b917524f6a0fb891
- https://git.kernel.org/stable/c/47dfac48bce7198ad4f1a388fc8c9491f878ac3b
- https://git.kernel.org/stable/c/4986410316b1ae0e63c6ce418e4eb196723626e7
- https://git.kernel.org/stable/c/64d7584e62ac8cdc750455c5fdc6008fc2de4f06
- https://git.kernel.org/stable/c/c292d4686f717c03e5022fc4ae7c782f39a94915
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74608.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
