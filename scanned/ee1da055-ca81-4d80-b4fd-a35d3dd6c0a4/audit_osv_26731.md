# [H] NFS: Fix a potential data corruption

## Summary
Severity: High
Advisory: CVE-2023-53711
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53711
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix a potential data corruption

We must ensure that the subrequests are joined back into the head before
we can retransmit a request. If the head was not on the commit lists,
because the server wrote it synchronously, we still need to add it back
to the retransmission list.
Add a call that mirrors the effect of nfs_cancel_remove_inode() for
O_DIRECT.

## References
- https://git.kernel.org/stable/c/0ec26716e45d615edfff46012e7dedcc0ac5f7ab
- https://git.kernel.org/stable/c/4185605cd0f72ec8bf8b423aacd94cd5ee13bbcf
- https://git.kernel.org/stable/c/88975a55969e11f26fe3846bf4fbf8e7dc8cbbd4
- https://git.kernel.org/stable/c/da302f1d476a44245823a74546debb5d160bf5bd
- https://git.kernel.org/stable/c/dac14a1dbe20e003215dacb8a3a1a7e4ca4e0ad0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53711.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53711
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
