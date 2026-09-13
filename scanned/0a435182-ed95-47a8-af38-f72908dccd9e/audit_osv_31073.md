# [H] iio: dummy: iio_simply_dummy_buffer: fix information leak in triggered buffer

## Summary
Severity: High
Advisory: CVE-2024-57911
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57911
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: dummy: iio_simply_dummy_buffer: fix information leak in triggered buffer

The 'data' array is allocated via kmalloc() and it is used to push data
to user space from a triggered buffer, but it does not set values for
inactive channels, as it only uses iio_for_each_active_channel()
to assign new values.

Use kzalloc for the memory allocation to avoid pushing uninitialized
information to userspace.

## References
- https://git.kernel.org/stable/c/006073761888a632c5d6f93e47c41760fa627f77
- https://git.kernel.org/stable/c/03fa47621bf8fcbf5994c5716021527853f9af3d
- https://git.kernel.org/stable/c/333be433ee908a53f283beb95585dfc14c8ffb46
- https://git.kernel.org/stable/c/74058395b2c63c8a438cf199d09094b640f8c7f4
- https://git.kernel.org/stable/c/b0642d9c871aea1f28eb02cd84d60434df594f67
- https://git.kernel.org/stable/c/e1c1e8c05010103c9c9ea3e9c4304b0b7e2c8e4a
- https://git.kernel.org/stable/c/ea703cda36da0dacb9a2fd876370003197d8a019
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57911.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
