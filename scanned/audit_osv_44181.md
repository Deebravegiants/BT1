# [H] s390/vfio_ccw: Cancel existing workqueues

## Summary
Severity: High
Advisory: CVE-2026-80553
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80553
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Cancel existing workqueues

The initialization of the io_work and crw_work workqueues begs the
question of whether they should be un-initialized. Add the corresponding
cleanup tags in _release_dev to ensure work isn't dispatched after
the private struct is free'd.

## References
- https://git.kernel.org/stable/c/7492ca2d0c5d59add01e267be9f5a6eeb8076fd7
- https://git.kernel.org/stable/c/77f5e888d2e607a0b3141fb95091ad6ef1cca9a2
- https://git.kernel.org/stable/c/79c60b2c61105368dcc8444eb45847e21734f7c4
- https://git.kernel.org/stable/c/87d569cb35a541b31a184faf982540694d4c9a89
- https://git.kernel.org/stable/c/b7ae0f7993867d009a4b554fc1d6d451c10580a0
- https://git.kernel.org/stable/c/b94b28c1f0fae53b2f2d6180ae6442c9a1558f67
- https://git.kernel.org/stable/c/dc47a98abe6714577a25224534dbd356051097a3
- https://git.kernel.org/stable/c/e868ea8be0bc88c6982f48ecf3259d98afd884ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80553.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80553
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
