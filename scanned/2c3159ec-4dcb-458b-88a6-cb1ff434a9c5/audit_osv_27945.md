# [M] nvme-fc: do not wait in vain when unloading module

## Summary
Severity: Medium
Advisory: CVE-2024-26846
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26846
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-fc: do not wait in vain when unloading module

The module exit path has race between deleting all controllers and
freeing 'left over IDs'. To prevent double free a synchronization
between nvme_delete_ctrl and ida_destroy has been added by the initial
commit.

There is some logic around trying to prevent from hanging forever in
wait_for_completion, though it does not handling all cases. E.g.
blktests is able to reproduce the situation where the module unload
hangs forever.

If we completely rely on the cleanup code executed from the
nvme_delete_ctrl path, all IDs will be freed eventually. This makes
calling ida_destroy unnecessary. We only have to ensure that all
nvme_delete_ctrl code has been executed before we leave
nvme_fc_exit_module. This is done by flushing the nvme_delete_wq
workqueue.

While at it, remove the unused nvme_fc_wq workqueue too.

## References
- https://git.kernel.org/stable/c/085195aa90a924c79e35569bcdad860d764a8e17
- https://git.kernel.org/stable/c/0bf567d6d9ffe09e059bbdfb4d07143cef42c75c
- https://git.kernel.org/stable/c/4f2c95015ec2a1899161be6c0bdaecedd5a7bfb2
- https://git.kernel.org/stable/c/70fbfc47a392b98e5f8dba70c6efc6839205c982
- https://git.kernel.org/stable/c/baa6b7eb8c66486bd64608adc63fe03b30d3c0b9
- https://git.kernel.org/stable/c/c0882c366418bf9c19e1ba7f270fe377a9bf5d67
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26846.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26846
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
