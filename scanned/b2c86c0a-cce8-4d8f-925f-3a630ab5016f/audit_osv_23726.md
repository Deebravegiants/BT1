# [M] serial: 8250_aspeed_vuart: Fix potential NULL dereference in aspeed_vuart_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49392
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49392
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: 8250_aspeed_vuart: Fix potential NULL dereference in aspeed_vuart_probe

platform_get_resource() may fail and return NULL, so we should
better check it's return value to avoid a NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/0e0fd55719fa081de6f9e5d9e6cef48efb04d34a
- https://git.kernel.org/stable/c/90a6b6fc52bfdcfe9698454bf5bea26112abbcd1
- https://git.kernel.org/stable/c/923d34ce069e8e51a4d003caa6b66a8cd6ecd0ed
- https://git.kernel.org/stable/c/d5f1275f101e0e8a172d300d897f5a12e87e3485
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49392.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
