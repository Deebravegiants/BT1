# [H] net: seeq: Fix use after free vulnerability in ether3 Driver Due to Race Condition

## Summary
Severity: High
Advisory: CVE-2024-47747
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47747
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: seeq: Fix use after free vulnerability in ether3 Driver Due to Race Condition

In the ether3_probe function, a timer is initialized with a callback
function ether3_ledoff, bound to &prev(dev)->timer. Once the timer is
started, there is a risk of a race condition if the module or device
is removed, triggering the ether3_remove function to perform cleanup.
The sequence of operations that may lead to a UAF bug is as follows:

CPU0                                    CPU1

                      |  ether3_ledoff
ether3_remove         |
  free_netdev(dev);   |
  put_devic           |
  kfree(dev);         |
 |  ether3_outw(priv(dev)->regs.config2 |= CFG2_CTRLO, REG_CONFIG2);
                      | // use dev

Fix it by ensuring that the timer is canceled before proceeding with
the cleanup in ether3_remove.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/1c57d61a43293252ad732007c7070fdb112545fd
- https://git.kernel.org/stable/c/25d559ed2beec9b34045886100dac46d1ad92eba
- https://git.kernel.org/stable/c/338a0582b28e69460df03af50e938b86b4206353
- https://git.kernel.org/stable/c/516dbc6d16637430808c39568cbb6b841d32b55b
- https://git.kernel.org/stable/c/77a77331cef0a219b8dd91361435eeef04cb741c
- https://git.kernel.org/stable/c/822c7bb1f6f8b0331e8d1927151faf8db3b33afd
- https://git.kernel.org/stable/c/b5109b60ee4fcb2f2bb24f589575e10cc5283ad4
- https://git.kernel.org/stable/c/b5a84b6c772564c8359a9a0fbaeb2a2944aa1ee9
- https://git.kernel.org/stable/c/d2abc379071881798d20e2ac1d332ad855ae22f3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47747.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
