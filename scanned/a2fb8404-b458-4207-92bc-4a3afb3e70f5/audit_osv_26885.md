# [H] scsi: message: mptlan: Fix use after free bug in mptlan_remove() due to race condition

## Summary
Severity: High
Advisory: CVE-2023-54310
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54310
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: message: mptlan: Fix use after free bug in mptlan_remove() due to race condition

mptlan_probe() calls mpt_register_lan_device() which initializes the
&priv->post_buckets_task workqueue. A call to
mpt_lan_wake_post_buckets_task() will subsequently start the work.

During driver unload in mptlan_remove() the following race may occur:

CPU0                  CPU1

                    |mpt_lan_post_receive_buckets_work()
mptlan_remove()     |
  free_netdev()     |
    kfree(dev);     |
                    |
                    | dev->mtu
                    |   //use

Fix this by finishing the work prior to cleaning up in mptlan_remove().

[mkp: we really should remove mptlan instead of attempting to fix it]

## References
- https://git.kernel.org/stable/c/410e610a96c52a7b41e2ab6c9ca60868d9acecce
- https://git.kernel.org/stable/c/48daa4a3015d859ee424948844ce3c12f2fe44e6
- https://git.kernel.org/stable/c/60c8645ad6f5b722615383d595d63b62b07a13c3
- https://git.kernel.org/stable/c/697f92f8317e538d8409a0c95d6370eb40b34c05
- https://git.kernel.org/stable/c/92f869693d84e813895ff4d25363744575515423
- https://git.kernel.org/stable/c/9c6da3b7f12528cd52c458b33496a098b838fcfc
- https://git.kernel.org/stable/c/e84282efc87f2414839f6e15c31b4daa34ebaac1
- https://git.kernel.org/stable/c/f486893288f3e9b171b836f43853a6426515d800
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54310.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54310
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
