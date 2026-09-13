# [H] i3c: master: svc: Fix use after free vulnerability in svc_i3c_master Driver Due to Race Condition

## Summary
Severity: High
Advisory: CVE-2024-49874
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49874
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: master: svc: Fix use after free vulnerability in svc_i3c_master Driver Due to Race Condition

In the svc_i3c_master_probe function, &master->hj_work is bound with
svc_i3c_master_hj_work, &master->ibi_work is bound with
svc_i3c_master_ibi_work. And svc_i3c_master_ibi_work  can start the
hj_work, svc_i3c_master_irq_handler can start the ibi_work.

If we remove the module which will call svc_i3c_master_remove to
make cleanup, it will free master->base through i3c_master_unregister
while the work mentioned above will be used. The sequence of operations
that may lead to a UAF bug is as follows:

CPU0                                         CPU1

                                    | svc_i3c_master_hj_work
svc_i3c_master_remove               |
i3c_master_unregister(&master->base)|
device_unregister(&master->dev)     |
device_release                      |
//free master->base                 |
                                    | i3c_master_do_daa(&master->base)
                                    | //use master->base

Fix it by ensuring that the work is canceled before proceeding with the
cleanup in svc_i3c_master_remove.

## References
- https://git.kernel.org/stable/c/27b55724d3f781dd6e635e89dc6e2fd78fa81a00
- https://git.kernel.org/stable/c/4318998892bf8fe99f97bea18c37ae7b685af75a
- https://git.kernel.org/stable/c/4ac637122930cc4ab7e2c22e364cf3aaf96b05b1
- https://git.kernel.org/stable/c/56bddf543d4d7ddeff3f87b554ddacfdf086bffe
- https://git.kernel.org/stable/c/61850725779709369c7e907ae8c7c75dc7cec4f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49874.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
