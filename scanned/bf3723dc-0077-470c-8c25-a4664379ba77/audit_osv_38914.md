# [H] net: mana: fix use-after-free in add_adev() error path

## Summary
Severity: High
Advisory: CVE-2026-43056
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43056
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: fix use-after-free in add_adev() error path

If auxiliary_device_add() fails, add_adev() jumps to add_fail and calls
auxiliary_device_uninit(adev).

The auxiliary device has its release callback set to adev_release(),
which frees the containing struct mana_adev. Since adev is embedded in
struct mana_adev, the subsequent fall-through to init_fail and access
to adev->id may result in a use-after-free.

Fix this by saving the allocated auxiliary device id in a local
variable before calling auxiliary_device_add(), and use that saved id
in the cleanup path after auxiliary_device_uninit().

## References
- https://git.kernel.org/stable/c/43f5b19fd190fea20d052bc84741b28031d5baa9
- https://git.kernel.org/stable/c/5f4061f8225d18695e5afe9bbf1cb7bd673d7872
- https://git.kernel.org/stable/c/c4ea7d8907cf72b259bf70bd8c2e791e1c4ff70f
- https://git.kernel.org/stable/c/d88541ffd56d62a61e77209080001eddd4d69815
- https://git.kernel.org/stable/c/e5a75bf026c686b91a7dc6f9c5caf5016745d1fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43056.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
