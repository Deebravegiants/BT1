# [H] hwmon: (pmbus) Fix passing events to regulator core

## Summary
Severity: High
Advisory: CVE-2026-72395
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72395
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus) Fix passing events to regulator core

Sashiko reports:

Commit 754bd2b4a084 ("hwmon: (pmbus/core) Protect regulator operations with
mutex") introduced a worker to batch regulator events over time using
atomic_or(). The delayed worker then passes the combined bitmask unmodified
to regulator_notifier_call_chain().

The core regulator subsystem's regulator_handle_critical() function
evaluates the event parameter using a strict switch statement. If
multiple distinct faults occur before the worker runs (e.g.,
REGULATOR_EVENT_UNDER_VOLTAGE | REGULATOR_EVENT_OVER_CURRENT), the combined
bitmask fails to match any case. This leaves the reason as NULL and
completely bypasses the critical hw_protection_trigger().

Fix the problem by passing events bit by bit to the regulator event
handler.

## References
- https://git.kernel.org/stable/c/2106bf4056858fcce3624e0c51f6fee4d41d3f2f
- https://git.kernel.org/stable/c/489291b6b56978cc50d34e8e13f9636ea296ba8a
- https://git.kernel.org/stable/c/48fe43666950efefb7ac5fbdc012c1b3604096bf
- https://git.kernel.org/stable/c/9ef7dacd44216bf5ea05c8aef49eba4d145f4047
- https://git.kernel.org/stable/c/b0ff6b6ae9c5183ef701ece7016698bde5a5bfba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72395.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
