# [C] firmware: arm_ffa: Snapshot notifier callbacks under lock

## Summary
Severity: Critical
Advisory: CVE-2026-64080
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64080
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_ffa: Snapshot notifier callbacks under lock

Both notification handlers currently look up a notifier callback under
notify_lock, drop the lock, and then dereference the returned
notifier entry. A concurrent unregister can delete and free that
entry in the gap, leaving the handler to dereference stale memory.

Copy the callback pointer and callback data while notify_lock is
still held and invoke the callback only after the lock is dropped.
This keeps the existing callback execution model while removing the
use-after-free window in both the framework and non-framework
notification paths.

## References
- https://git.kernel.org/stable/c/0e7be42ef2490f19d859a6146324d48cafdc9d5c
- https://git.kernel.org/stable/c/38290b180a4d5746baed796d49f88d56d2f336cd
- https://git.kernel.org/stable/c/d1e38551fadea230649bc428f0f35c9ee062a072
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64080.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
