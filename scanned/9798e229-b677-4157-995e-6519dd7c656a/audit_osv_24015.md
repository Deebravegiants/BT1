# [M] HID: hyperv: fix possible memory leak in mousevsc_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49874
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49874
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: hyperv: fix possible memory leak in mousevsc_probe()

If hid_add_device() returns error, it should call hid_destroy_device()
to free hid_dev which is allocated in hid_allocate_device().

## References
- https://git.kernel.org/stable/c/249b743801c00542e9324f87b380032e957a43e8
- https://git.kernel.org/stable/c/5ad95d71344b7ffec360d62591633b3c465dc049
- https://git.kernel.org/stable/c/5f3aba6566b866f5b0a4916f0b2e8a6ae66a6451
- https://git.kernel.org/stable/c/8597b59e3d22b27849bd3e4f92a3d466774bfb04
- https://git.kernel.org/stable/c/a6d2fb1874c52ace1f5cf1966ee558829c5c19b6
- https://git.kernel.org/stable/c/b5bcb94b0954a026bbd671741fdb00e7141f9c91
- https://git.kernel.org/stable/c/e29289d0d8193fca6d2c1f0a1de75cfc80edec00
- https://git.kernel.org/stable/c/ed75d1a1c31a0cae8ecc8bcea710b25c0be68da0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49874.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
