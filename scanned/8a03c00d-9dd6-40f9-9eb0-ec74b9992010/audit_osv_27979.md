# [H] usb: ulpi: Fix debugfs directory leak

## Summary
Severity: High
Advisory: CVE-2024-26919
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26919
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: ulpi: Fix debugfs directory leak

The ULPI per-device debugfs root is named after the ulpi device's
parent, but ulpi_unregister_interface tries to remove a debugfs
directory named after the ulpi device itself. This results in the
directory sticking around and preventing subsequent (deferred) probes
from succeeding. Change the directory name to match the ulpi device.

## References
- https://git.kernel.org/stable/c/330d22aba17a4d30a56f007d0f51291d7e00862b
- https://git.kernel.org/stable/c/33713945cc92ea9c4a1a9479d5c1b7acb7fc4df3
- https://git.kernel.org/stable/c/3caf2b2ad7334ef35f55b95f3e1b138c6f77b368
- https://git.kernel.org/stable/c/d31b886ed6a5095214062ee4fb55037eb930adb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26919.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
