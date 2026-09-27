# [C] RDMA/srp: Do not call scsi_done() from srp_abort()

## Summary
Severity: Critical
Advisory: CVE-2023-52515
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52515
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.199, >=5.11.0 <5.15.136, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/srp: Do not call scsi_done() from srp_abort()

After scmd_eh_abort_handler() has called the SCSI LLD eh_abort_handler
callback, it performs one of the following actions:
* Call scsi_queue_insert().
* Call scsi_finish_command().
* Call scsi_eh_scmd_add().
Hence, SCSI abort handlers must not call scsi_done(). Otherwise all
the above actions would trigger a use-after-free. Hence remove the
scsi_done() call from srp_abort(). Keep the srp_free_req() call
before returning SUCCESS because we may not see the command again if
SUCCESS is returned.

## References
- https://git.kernel.org/stable/c/05a10b316adaac1f322007ca9a0383b410d759cc
- https://git.kernel.org/stable/c/26788a5b48d9d5cd3283d777d238631c8cd7495a
- https://git.kernel.org/stable/c/2b298f9181582270d5e95774e5a6c7a7fb5b1206
- https://git.kernel.org/stable/c/b9bdffb3f9aaeff8379c83f5449c6b42cb71c2b5
- https://git.kernel.org/stable/c/e193b7955dfad68035b983a0011f4ef3590c85eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52515.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52515
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
