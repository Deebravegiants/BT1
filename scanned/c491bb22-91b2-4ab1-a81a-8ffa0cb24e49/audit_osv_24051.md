# [M] net: dsa: Fix possible memory leaks in dsa_loop_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49926
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49926
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: Fix possible memory leaks in dsa_loop_init()

kmemleak reported memory leaks in dsa_loop_init():

kmemleak: 12 new suspected memory leaks

unreferenced object 0xffff8880138ce000 (size 2048):
  comm "modprobe", pid 390, jiffies 4295040478 (age 238.976s)
  backtrace:
    [<000000006a94f1d5>] kmalloc_trace+0x26/0x60
    [<00000000a9c44622>] phy_device_create+0x5d/0x970
    [<00000000d0ee2afc>] get_phy_device+0xf3/0x2b0
    [<00000000dca0c71f>] __fixed_phy_register.part.0+0x92/0x4e0
    [<000000008a834798>] fixed_phy_register+0x84/0xb0
    [<0000000055223fcb>] dsa_loop_init+0xa9/0x116 [dsa_loop]
    ...

There are two reasons for memleak in dsa_loop_init().

First, fixed_phy_register() create and register phy_device:

fixed_phy_register()
  get_phy_device()
    phy_device_create() # freed by phy_device_free()
  phy_device_register() # freed by phy_device_remove()

But fixed_phy_unregister() only calls phy_device_remove().
So the memory allocated in phy_device_create() is leaked.

Second, when mdio_driver_register() fail in dsa_loop_init(),
it just returns and there is no cleanup for phydevs.

Fix the problems by catching the error of mdio_driver_register()
in dsa_loop_init(), then calling both fixed_phy_unregister() and
phy_device_free() to release phydevs.
Also add a function for phydevs cleanup to avoid duplacate.

## References
- https://git.kernel.org/stable/c/37a098fc9b42bd7fce66764866aa514639667b6e
- https://git.kernel.org/stable/c/4d2024b138d9f7b02ae13ee997fd3a71e9e46254
- https://git.kernel.org/stable/c/633efc8b3dc96f56f5a57f2a49764853a2fa3f50
- https://git.kernel.org/stable/c/935b4beb724946a37cebf97191592d4879d3a3a3
- https://git.kernel.org/stable/c/9f555b1584fc2d5d16ee3c4d9438e93ac7c502c7
- https://git.kernel.org/stable/c/bbc5d7b46a729bfcbb5544f6612b7a67dd4f4d6f
- https://git.kernel.org/stable/c/d593e1ede655b74c42e4e4fe285ea64aee96fb5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49926.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
