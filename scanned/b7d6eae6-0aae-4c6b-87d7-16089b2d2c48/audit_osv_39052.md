# [H] iio: chemical: sps30_i2c: fix buffer size in sps30_i2c_read_meas()

## Summary
Severity: High
Advisory: CVE-2026-43476
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-43476
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: chemical: sps30_i2c: fix buffer size in sps30_i2c_read_meas()

sizeof(num) evaluates to sizeof(size_t) (8 bytes on 64-bit) instead
of the intended __be32 element size (4 bytes). Use sizeof(*meas) to
correctly match the buffer element type.

## References
- https://git.kernel.org/stable/c/08881d82f94deaa51800360029908863e5c4c39d
- https://git.kernel.org/stable/c/165f12b40901c6a7aca15796da239726ddcdc5ad
- https://git.kernel.org/stable/c/216345f98cae7fcc84f49728c67478ac00321c87
- https://git.kernel.org/stable/c/2a4d111a6a34afb8bb4f118009e7728ed2ec7e10
- https://git.kernel.org/stable/c/90e978ace598567e6e30de79805bddf37cf892ac
- https://git.kernel.org/stable/c/9aff2e9c2927ecd9652872a43a0725f101128104
- https://git.kernel.org/stable/c/dcdf1e92674efb6692f4ebe189e0aa9fde23a541
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43476.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43476
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
