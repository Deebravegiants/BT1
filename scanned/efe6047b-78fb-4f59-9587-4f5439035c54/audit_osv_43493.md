# [H] kcm: use WRITE_ONCE() when changing lower socket callbacks

## Summary
Severity: High
Advisory: CVE-2026-74262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74262
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

kcm: use WRITE_ONCE() when changing lower socket callbacks

kcm_attach() replaces a live lower TCP socket's sk_data_ready and
sk_write_space callbacks with KCM handlers, and kcm_unattach() restores
them later. Those callback-pointer updates are still plain stores even
though the same fields can be read and invoked concurrently on other
CPUs.

If another CPU observes an older callback snapshot after the live field
has already been restored, callback execution can run with a mismatched
target and sk_user_data state, leading to stale or misdirected wakeups.

Use WRITE_ONCE() for the callback replacement and restore operations so
these shared callback fields follow the same visibility contract already
established by the earlier 4022 fixes.

## References
- https://git.kernel.org/stable/c/0cb3e2f40679032c1aa2186280a86e5ead0161ee
- https://git.kernel.org/stable/c/11faefd11ce2448bac7279ab302dd1954a6547fe
- https://git.kernel.org/stable/c/47186409c092cd7dd70350999186c700233e854d
- https://git.kernel.org/stable/c/9684fff87124b201e11dea01ded9173025359a0f
- https://git.kernel.org/stable/c/b4ccd6eef671d7c44a30123cd29f3acf3de8468e
- https://git.kernel.org/stable/c/b8c90823cdfb5f3d22f261aeb3e9066612853c36
- https://git.kernel.org/stable/c/f01fb6138f8eb606b56ce9158e2d8b72352c53f4
- https://git.kernel.org/stable/c/fa26e4606aed0f7fe793c325506adeda1d847a43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
