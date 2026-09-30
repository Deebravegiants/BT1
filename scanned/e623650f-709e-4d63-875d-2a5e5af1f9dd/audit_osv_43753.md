# [H] watchdog: at91sam9_wdt: prevent timer rearm during teardown

## Summary
Severity: High
Advisory: CVE-2026-74687
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74687
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

watchdog: at91sam9_wdt: prevent timer rearm during teardown

at91_ping() rearms the watchdog timer from its callback. timer_delete()
neither waits for a running callback nor prevents it from rearming the
timer, so probe failure or driver removal can leave the timer accessing the
devm-allocated at91wdt after it has been freed.

Use timer_shutdown_sync() on both teardown paths. It waits for a running
callback and rejects any attempt by the callback to rearm the timer.

## References
- https://git.kernel.org/stable/c/29fe74c9aa69d78c1c6a3930f1d9fc5db71a6eed
- https://git.kernel.org/stable/c/8444d66aa6b6e7fe0a26fa1a00a11cb4d0523783
- https://git.kernel.org/stable/c/b7949b0a7d998013b7ec8617a0ef5b07cca80be4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74687.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74687
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
