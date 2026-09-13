# [H] hwmon: (pmbus/core) Protect regulator operations with mutex

## Summary
Severity: High
Advisory: CVE-2026-31486
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31486
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <6.6.143, >=6.7.0 <6.12.92, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus/core) Protect regulator operations with mutex

The regulator operations pmbus_regulator_get_voltage(),
pmbus_regulator_set_voltage(), and pmbus_regulator_list_voltage()
access PMBus registers and shared data but were not protected by
the update_lock mutex. This could lead to race conditions.

However, adding mutex protection directly to these functions causes
a deadlock because pmbus_regulator_notify() (which calls
regulator_notifier_call_chain()) is often called with the mutex
already held (e.g., from pmbus_fault_handler()). If a regulator
callback then calls one of the now-protected voltage functions,
it will attempt to acquire the same mutex.

Rework pmbus_regulator_notify() to utilize a worker function to
send notifications outside of the mutex protection. Events are
stored as atomics in a per-page bitmask and processed by the worker.

Initialize the worker and its associated data during regulator
registration, and ensure it is cancelled on device removal using
devm_add_action_or_reset().

While at it, remove the unnecessary include of linux/of.h.

## References
- https://git.kernel.org/stable/c/2c77ae315f3ce9d2c8e1609be74c9358c1fe4e07
- https://git.kernel.org/stable/c/4e9d723d9f198b86f6882a84c501ba1f39e8d055
- https://git.kernel.org/stable/c/754bd2b4a084b90b5e7b630e1f423061a9b9b761
- https://git.kernel.org/stable/c/acf04e2863132f6d9222f71f3a76fb9782cbe061
- https://git.kernel.org/stable/c/b26849cffaa7c43355b82e9bef3725e786973a1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31486.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31486
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
