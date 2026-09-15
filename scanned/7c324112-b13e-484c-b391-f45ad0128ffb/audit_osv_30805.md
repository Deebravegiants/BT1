# [M] ad7780: fix division by zero in ad7780_write_raw()

## Summary
Severity: Medium
Advisory: CVE-2024-56567
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56567
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ad7780: fix division by zero in ad7780_write_raw()

In the ad7780_write_raw() , val2 can be zero, which might lead to a
division by zero error in DIV_ROUND_CLOSEST(). The ad7780_write_raw()
is based on iio_info's write_raw. While val is explicitly declared that
can be zero (in read mode), val2 is not specified to be non-zero.

## References
- https://git.kernel.org/stable/c/022e13518ba6cc1b4fdd291f49e4f57b2d5718e0
- https://git.kernel.org/stable/c/18fb33df1de83a014d7f784089f9b124facc157f
- https://git.kernel.org/stable/c/68e79b848196a0b0ec006009cc69da1f835d1ae8
- https://git.kernel.org/stable/c/7e3a8ea3d1ada7f707de5d9d504774b4191eab66
- https://git.kernel.org/stable/c/afc1e3c00b3f5f0b4f1bc3e974fb9803cb938a90
- https://git.kernel.org/stable/c/c174b53e95adf2eece2afc56cd9798374919f99a
- https://git.kernel.org/stable/c/f25a9f1df1f6738acf1fa05595fb6060a2c08ff1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56567.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56567
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
