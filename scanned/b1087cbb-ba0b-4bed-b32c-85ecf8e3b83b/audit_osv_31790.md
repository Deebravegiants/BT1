# [M] gpiolib: Fix crash on error in gpiochip_get_ngpios()

## Summary
Severity: Medium
Advisory: CVE-2025-21783
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21783
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpiolib: Fix crash on error in gpiochip_get_ngpios()

The gpiochip_get_ngpios() uses chip_*() macros to print messages.
However these macros rely on gpiodev to be initialised and set,
which is not the case when called via bgpio_init(). In such a case
the printing messages will crash on NULL pointer dereference.
Replace chip_*() macros by the respective dev_*() ones to avoid
such crash.

## References
- https://git.kernel.org/stable/c/189fb76215e479c10731baabb50f1a352d2078f5
- https://git.kernel.org/stable/c/4d9b2b62e1136d10f661ec4c0c268140b6f74f4f
- https://git.kernel.org/stable/c/7b4aebeecbbd5b5fe73e35fad3f62ed21aa7ef44
- https://git.kernel.org/stable/c/a7052afa9eae2239e25943baa8817a6a56e8aa68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21783.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21783
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
