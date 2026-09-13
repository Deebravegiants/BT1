# [M] gpiolib: cdev: Set lineevent_state::irq after IRQ register successfully

## Summary
Severity: Medium
Advisory: CVE-2022-48660
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48660
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.146, >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpiolib: cdev: Set lineevent_state::irq after IRQ register successfully

When running gpio test on nxp-ls1028 platform with below command
gpiomon --num-events=3 --rising-edge gpiochip1 25
There will be a warning trace as below:
Call trace:
free_irq+0x204/0x360
lineevent_free+0x64/0x70
gpio_ioctl+0x598/0x6a0
__arm64_sys_ioctl+0xb4/0x100
invoke_syscall+0x5c/0x130
......
el0t_64_sync+0x1a0/0x1a4
The reason of this issue is that calling request_threaded_irq()
function failed, and then lineevent_free() is invoked to release
the resource. Since the lineevent_state::irq was already set, so
the subsequent invocation of free_irq() would trigger the above
warning call trace. To fix this issue, set the lineevent_state::irq
after the IRQ register successfully.

## References
- https://git.kernel.org/stable/c/657803b918e097e47d99d1489da83a603c36bcdd
- https://git.kernel.org/stable/c/69bef19d6b9700e96285f4b4e28691cda3dcd0d1
- https://git.kernel.org/stable/c/97da736cd11ae73bdf2f5e21e24446b8349e0168
- https://git.kernel.org/stable/c/b1489043d3b9004dd8d5a0357b08b5f0e6691c43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48660.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48660
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
