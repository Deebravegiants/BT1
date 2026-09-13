# [H] can: bcm: switch timer to HRTIMER_MODE_SOFT and remove hrtimer_tasklet

## Summary
Severity: High
Advisory: CVE-2026-17523
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17523
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: switch timer to HRTIMER_MODE_SOFT and remove hrtimer_tasklet

This patch switches the timer to HRTIMER_MODE_SOFT, which executed the
timer callback in softirq context and removes the hrtimer_tasklet.

## References
- https://git.kernel.org/stable/c/79305a826f872fe446c6fbf8450f515053ef6951
- https://git.kernel.org/stable/c/bf74aa86e111aa3b2fbb25db37e3a3fab71b5b68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17523.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17523
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
