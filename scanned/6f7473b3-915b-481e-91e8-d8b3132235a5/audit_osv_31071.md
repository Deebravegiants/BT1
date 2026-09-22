# [H] iio: imu: kmx61: fix information leak in triggered buffer

## Summary
Severity: High
Advisory: CVE-2024-57908
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57908
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: imu: kmx61: fix information leak in triggered buffer

The 'buffer' local array is used to push data to user space from a
triggered buffer, but it does not set values for inactive channels, as
it only uses iio_for_each_active_channel() to assign new values.

Initialize the array to zero before using it to avoid pushing
uninitialized information to userspace.

## References
- https://git.kernel.org/stable/c/0871eb8d700b33dd7fa86c80630d62ddaef58c2c
- https://git.kernel.org/stable/c/565814cbbaa674d2901428796801de49a611e59d
- https://git.kernel.org/stable/c/6985ba4467e4b15b809043fa7740d1fb23a1897b
- https://git.kernel.org/stable/c/6ae053113f6a226a2303caa4936a4c37f3bfff7b
- https://git.kernel.org/stable/c/a07f698084412a3ef5e950fcac1d6b0f53289efd
- https://git.kernel.org/stable/c/a386d9d2dc6635f2ec210b8199cfb3acf4d31305
- https://git.kernel.org/stable/c/cde312e257b59ecaa0fad3af9ec7e2370bb24639
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57908.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
