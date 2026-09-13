# [H] HID: roccat: fix use-after-free in roccat_report_event

## Summary
Severity: High
Advisory: CVE-2026-43111
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43111
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: roccat: fix use-after-free in roccat_report_event

roccat_report_event() iterates over the device->readers list without
holding the readers_lock. This allows a concurrent roccat_release() to
remove and free a reader while it's still being accessed, leading to a
use-after-free.

Protect the readers list traversal with the readers_lock mutex.

## References
- https://git.kernel.org/stable/c/181ea51ab0f6370842c5b49cfb86824253a1189e
- https://git.kernel.org/stable/c/20dca865460f7943cf70afca274b60dac371f546
- https://git.kernel.org/stable/c/36bb2d0b915014bbdc5044982b31b57b78045b93
- https://git.kernel.org/stable/c/441689e3103694caa3e2d62b7d57c7bccefa5e37
- https://git.kernel.org/stable/c/bca0b595e15450dd66b1153c76c4ef1087ee011b
- https://git.kernel.org/stable/c/d802d848308b35220f21a8025352f0c0aba15c12
- https://git.kernel.org/stable/c/e16a6d11bd77b81632165f02cf0d5946df74b3b7
- https://git.kernel.org/stable/c/e6a445513fbc6a0329d2d5ff375b6725750ec5a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
