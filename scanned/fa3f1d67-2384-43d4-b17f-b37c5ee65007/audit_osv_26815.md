# [H] power: supply: bq27xxx: Fix poll_interval handling and races on remove

## Summary
Severity: High
Advisory: CVE-2023-54079
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54079
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.114, >=5.16.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: bq27xxx: Fix poll_interval handling and races on remove

Before this patch bq27xxx_battery_teardown() was setting poll_interval = 0
to avoid bq27xxx_battery_update() requeuing the delayed_work item.

There are 2 problems with this:

1. If the driver is unbound through sysfs, rather then the module being
   rmmod-ed, this changes poll_interval unexpectedly

2. This is racy, after it being set poll_interval could be changed
   before bq27xxx_battery_update() checks it through
   /sys/module/bq27xxx_battery/parameters/poll_interval

Fix this by added a removed attribute to struct bq27xxx_device_info and
using that instead of setting poll_interval to 0.

There also is another poll_interval related race on remove(), writing
/sys/module/bq27xxx_battery/parameters/poll_interval will requeue
the delayed_work item for all devices on the bq27xxx_battery_devices
list and the device being removed was only removed from that list
after cancelling the delayed_work item.

Fix this by moving the removal from the bq27xxx_battery_devices list
to before cancelling the delayed_work item.

## References
- https://git.kernel.org/stable/c/0c5f4cec759679c290720fbcf6bb81768e21c95b
- https://git.kernel.org/stable/c/465d919151a1e8d40daf366b868914f59d073211
- https://git.kernel.org/stable/c/4c9615474fb0a41cfad658d78db3c9ec70912969
- https://git.kernel.org/stable/c/b12faeca0e819ea09051a705fef9df7ea7e9e18c
- https://git.kernel.org/stable/c/c00bc80462afc7963f449d7f21d896d2f629cacc
- https://git.kernel.org/stable/c/d952a1eaafcc5f0351caad5dbe9b5b3300d1d529
- https://git.kernel.org/stable/c/e85757da9091998276ff21a13915ac25229cc232
- https://git.kernel.org/stable/c/e98e5bebfcafc75a7b41192a607dfea5c1268afa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54079.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
