# [H] ASoC: sma1307: fix double free of devm_kzalloc() memory

## Summary
Severity: High
Advisory: CVE-2026-31475
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31475
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: sma1307: fix double free of devm_kzalloc() memory

A previous change added NULL checks and cleanup for allocation
failures in sma1307_setting_loaded().

However, the cleanup for mode_set entries is wrong. Those entries are
allocated with devm_kzalloc(), so they are device-managed resources and
must not be freed with kfree(). Manually freeing them in the error path
can lead to a double free when devres later releases the same memory.

Drop the manual kfree() loop and let devres handle the cleanup.

## References
- https://git.kernel.org/stable/c/1a82c3272626db9006f4c2cad3adf2916417aed6
- https://git.kernel.org/stable/c/d472d1a52985211b92883bb64bbe710b45980190
- https://git.kernel.org/stable/c/fe757092d2329c397ecb32f2bf68a5b1c4bd9193
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31475.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31475
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
