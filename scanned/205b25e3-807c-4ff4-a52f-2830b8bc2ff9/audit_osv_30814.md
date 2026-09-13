# [M] media: qcom: camss: fix error path on configuration of power domains

## Summary
Severity: Medium
Advisory: CVE-2024-56580
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56580
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: qcom: camss: fix error path on configuration of power domains

There is a chance to meet runtime issues during configuration of CAMSS
power domains, because on the error path dev_pm_domain_detach() is
unexpectedly called with NULL or error pointer.

One of the simplest ways to reproduce the problem is to probe CAMSS
driver before registration of CAMSS power domains, for instance if
a platform CAMCC driver is simply not built.

Warning backtrace example:

    Unable to handle kernel NULL pointer dereference at virtual address 00000000000001a2

    <snip>

    pc : dev_pm_domain_detach+0x8/0x48
    lr : camss_probe+0x374/0x9c0

    <snip>

    Call trace:
     dev_pm_domain_detach+0x8/0x48
     platform_probe+0x70/0xf0
     really_probe+0xc4/0x2a8
     __driver_probe_device+0x80/0x140
     driver_probe_device+0x48/0x170
     __device_attach_driver+0xc0/0x148
     bus_for_each_drv+0x88/0xf0
     __device_attach+0xb0/0x1c0
     device_initial_probe+0x1c/0x30
     bus_probe_device+0xb4/0xc0
     deferred_probe_work_func+0x90/0xd0
     process_one_work+0x164/0x3e0
     worker_thread+0x310/0x420
     kthread+0x120/0x130
     ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/4f45d65b781499d2a79eca12155532739c876aa2
- https://git.kernel.org/stable/c/c98586d8d01c9e860e7acc3807c2afeb1dc14e8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56580.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
