# [H] rpmsg: core: fix race in driver_override_show() and use core helper

## Summary
Severity: High
Advisory: CVE-2025-71274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2025-71274
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpmsg: core: fix race in driver_override_show() and use core helper

The driver_override_show function reads the driver_override string
without holding the device_lock. However, the store function modifies
and frees the string while holding the device_lock. This creates a race
condition where the string can be freed by the store function while
being read by the show function, leading to a use-after-free.

To fix this, replace the rpmsg_string_attr macro with explicit show and
store functions. The new driver_override_store uses the standard
driver_set_override helper. Since the introduction of
driver_set_override, the comments in include/linux/rpmsg.h have stated
that this helper must be used to set or clear driver_override, but the
implementation was not updated until now.

Because driver_set_override modifies and frees the string while holding
the device_lock, the new driver_override_show now correctly holds the
device_lock during the read operation to prevent the race.

Additionally, since rpmsg_string_attr has only ever been used for
driver_override, removing the macro simplifies the code.

## References
- https://git.kernel.org/stable/c/2e4a70f3c30910427e5ea848b799066d67b963d5
- https://git.kernel.org/stable/c/392c6b68334aa0e0ae9aba95c0a366bcb0d92f5d
- https://git.kernel.org/stable/c/42023d4b6d2661a40ee2dcf7e1a3528a35c638ca
- https://git.kernel.org/stable/c/47615557447185917afa432b7958f87583c417cb
- https://git.kernel.org/stable/c/7654e6e3cd6bdee9602f6063b3c670bd556d7e61
- https://git.kernel.org/stable/c/90c8353f471821d7ccd4fe573a2402e056192494
- https://git.kernel.org/stable/c/954557957177c3c13d7c655976665b1170da5e50
- https://git.kernel.org/stable/c/d66b8074c555e8abb0ae19eea1c9f3635498bdde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71274.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
