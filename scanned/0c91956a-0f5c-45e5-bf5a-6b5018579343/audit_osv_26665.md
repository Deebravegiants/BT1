# [H] virtio_net: Fix error unwinding of XDP initialization

## Summary
Severity: High
Advisory: CVE-2023-53499
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53499
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio_net: Fix error unwinding of XDP initialization

When initializing XDP in virtnet_open(), some rq xdp initialization
may hit an error causing net device open failed. However, previous
rqs have already initialized XDP and enabled NAPI, which is not the
expected behavior. Need to roll back the previous rq initialization
to avoid leaks in error unwinding of init code.

Also extract helper functions of disable and enable queue pairs.
Use newly introduced disable helper function in error unwinding and
virtnet_close. Use enable helper function in virtnet_open.

## References
- https://git.kernel.org/stable/c/037768b28e3752c07d63d1c72a651a6775b080bb
- https://git.kernel.org/stable/c/5306623a9826aa7d63b32c6a3803c798a765474d
- https://git.kernel.org/stable/c/6a7690f2bd178eee80f33411ae32e543ae66379c
- https://git.kernel.org/stable/c/73f53bc295727a3cdbd9d6bcdfaa239258970cf4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53499.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53499
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
