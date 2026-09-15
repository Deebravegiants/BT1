# [M] watchdog: rzg2l_wdt: Fix 32bit overflow issue

## Summary
Severity: Medium
Advisory: CVE-2022-49387
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49387
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

watchdog: rzg2l_wdt: Fix 32bit overflow issue

The value of timer_cycle_us can be 0 due to 32bit overflow.
For eg:- If we assign the counter value "0xfff" for computing
maxval.

This patch fixes this issue by appending ULL to 1024, so that
it is promoted to 64bit.

This patch also fixes the warning message, 'watchdog: Invalid min and
max timeout values, resetting to 0!'.

## References
- https://git.kernel.org/stable/c/b95a47667d34e76c2c9013f8e3b1e5039a5a0b76
- https://git.kernel.org/stable/c/e07b9fa0dc32b492de85528caaf9f0c605d8424f
- https://git.kernel.org/stable/c/ea2949df22a533cdf75e4583c00b1ce94cd5a83b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49387.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
