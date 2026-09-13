# [H] irqchip/qcom-mpm: Prevent crash when trying to handle non-wake GPIOs

## Summary
Severity: High
Advisory: CVE-2025-37901
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37901
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/qcom-mpm: Prevent crash when trying to handle non-wake GPIOs

On Qualcomm chipsets not all GPIOs are wakeup capable. Those GPIOs do not
have a corresponding MPM pin and should not be handled inside the MPM
driver. The IRQ domain hierarchy is always applied, so it's required to
explicitly disconnect the hierarchy for those. The pinctrl-msm driver marks
these with GPIO_NO_WAKE_IRQ. qcom-pdc has a check for this, but
irq-qcom-mpm is currently missing the check. This is causing crashes when
setting up interrupts for non-wake GPIOs:

 root@rb1:~# gpiomon -c gpiochip1 10
   irq: IRQ159: trimming hierarchy from :soc@0:interrupt-controller@f200000-1
   Unable to handle kernel paging request at virtual address ffff8000a1dc3820
   Hardware name: Qualcomm Technologies, Inc. Robotics RB1 (DT)
   pc : mpm_set_type+0x80/0xcc
   lr : mpm_set_type+0x5c/0xcc
   Call trace:
    mpm_set_type+0x80/0xcc (P)
    qcom_mpm_set_type+0x64/0x158
    irq_chip_set_type_parent+0x20/0x38
    msm_gpio_irq_set_type+0x50/0x530
    __irq_set_trigger+0x60/0x184
    __setup_irq+0x304/0x6bc
    request_threaded_irq+0xc8/0x19c
    edge_detector_setup+0x260/0x364
    linereq_create+0x420/0x5a8
    gpio_ioctl+0x2d4/0x6c0

Fix this by copying the check for GPIO_NO_WAKE_IRQ from qcom-pdc.c, so that
MPM is removed entirely from the hierarchy for non-wake GPIOs.

## References
- https://git.kernel.org/stable/c/38a05c0b87833f5b188ae43b428b1f792df2b384
- https://git.kernel.org/stable/c/45aced97f01d5ab14c8a2a60f6748f18c501c3f5
- https://git.kernel.org/stable/c/d5c10448f411a925dd59005785cb971f0626e032
- https://git.kernel.org/stable/c/dfbaecf7e38f5e9bfa5e47a1e525ffbb58bab8cf
- https://git.kernel.org/stable/c/f102342360950b56959e5fff4a874ea88ae13758
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37901.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37901
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
