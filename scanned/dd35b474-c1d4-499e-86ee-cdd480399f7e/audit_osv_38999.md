# [H] iio: accel: adxl380: Avoid reading more entries than present in FIFO

## Summary
Severity: High
Advisory: CVE-2026-43307
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43307
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: accel: adxl380: Avoid reading more entries than present in FIFO

The interrupt handler reads FIFO entries in batches of N samples, where N
is the number of scan elements that have been enabled. However, the sensor
fills the FIFO one sample at a time, even when more than one channel is
enabled. Therefore,the number of entries reported by the FIFO status
registers may not be a multiple of N; if this number is not a multiple, the
number of entries read from the FIFO may exceed the number of entries
actually present.

To fix the above issue, round down the number of FIFO entries read from the
status registers so that it is always a multiple of N.

## References
- https://git.kernel.org/stable/c/a40f316085985f916ba1599fc303fdbc6a078e86
- https://git.kernel.org/stable/c/a8e88edfd69df7b63c882aa53e61e7c078806ad7
- https://git.kernel.org/stable/c/c1b14015224cfcccd5356333763f2f4f401bd810
- https://git.kernel.org/stable/c/f42ddb2945ae4ce2b6f1c2e7aae9f14455a734d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43307.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43307
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
