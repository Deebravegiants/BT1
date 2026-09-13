# [M] RDMA/cm: Fix memory leak in ib_cm_insert_listen

## Summary
Severity: Medium
Advisory: CVE-2022-49671
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49671
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.129, >=5.11.0 <5.15.53, >=5.16.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/cm: Fix memory leak in ib_cm_insert_listen

cm_alloc_id_priv() allocates resource for the cm_id_priv. When
cm_init_listen() fails it doesn't free it, leading to memory leak.

Add the missing error unwind.

## References
- https://git.kernel.org/stable/c/2990f223ffa7bb25422956b9f79f9176a5b38346
- https://git.kernel.org/stable/c/2febf09a8a8ae4accf908f043f1bab1421056568
- https://git.kernel.org/stable/c/889000874c1204e47c7f2a4945db262a47e7efc9
- https://git.kernel.org/stable/c/b0cab8b517aeaf2592c3479294f934209c41a26f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49671.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
