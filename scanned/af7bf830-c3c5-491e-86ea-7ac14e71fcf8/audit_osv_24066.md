# [H] ieee802154/adf7242: defer destroy_workqueue call

## Summary
Severity: High
Advisory: CVE-2022-49968
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49968
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.258, >=4.20.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ieee802154/adf7242: defer destroy_workqueue call

There is a possible race condition (use-after-free) like below

  (FREE)                     |  (USE)
  adf7242_remove             |  adf7242_channel
   cancel_delayed_work_sync  |
    destroy_workqueue (1)    |   adf7242_cmd_rx
                             |    mod_delayed_work (2)
                             |

The root cause for this race is that the upper layer (ieee802154) is
unaware of this detaching event and the function adf7242_channel can
be called without any checks.

To fix this, we can add a flag write at the beginning of adf7242_remove
and add flag check in adf7242_channel. Or we can just defer the
destructive operation like other commit 3e0588c291d6 ("hamradio: defer
ax25 kfree after unregister_netdev") which let the
ieee802154_unregister_hw() to handle the synchronization. This patch
takes the second option.

runs")

## References
- https://git.kernel.org/stable/c/15f3b89bd521d5770d36a61fc04a77c293138ba6
- https://git.kernel.org/stable/c/23a29932715ca43bceb2eae1bdb770995afe7271
- https://git.kernel.org/stable/c/9f8558c5c642c62c450c98c99b7d18a709fff485
- https://git.kernel.org/stable/c/afe7116f6d3b888778ed6d95e3cf724767b9aedf
- https://git.kernel.org/stable/c/bed12d7531df1417fc92c691999ff95e03835008
- https://git.kernel.org/stable/c/dede80aaf01f4b6e8657d23726cb4a3da226ec4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49968.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
