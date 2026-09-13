# [H] ax25: fix use-after-free bugs caused by ax25_ds_del_timer

## Summary
Severity: High
Advisory: CVE-2024-35887
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35887
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: fix use-after-free bugs caused by ax25_ds_del_timer

When the ax25 device is detaching, the ax25_dev_device_down()
calls ax25_ds_del_timer() to cleanup the slave_timer. When
the timer handler is running, the ax25_ds_del_timer() that
calls del_timer() in it will return directly. As a result,
the use-after-free bugs could happen, one of the scenarios
is shown below:

      (Thread 1)          |      (Thread 2)
                          | ax25_ds_timeout()
ax25_dev_device_down()    |
  ax25_ds_del_timer()     |
    del_timer()           |
  ax25_dev_put() //FREE   |
                          |  ax25_dev-> //USE

In order to mitigate bugs, when the device is detaching, use
timer_shutdown_sync() to stop the timer.

## References
- https://git.kernel.org/stable/c/74204bf9050f7627aead9875fe4e07ba125cb19b
- https://git.kernel.org/stable/c/c6a368f9c7af4c14b14d390c2543af8001c9bdb9
- https://git.kernel.org/stable/c/fd819ad3ecf6f3c232a06b27423ce9ed8c20da89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35887.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
