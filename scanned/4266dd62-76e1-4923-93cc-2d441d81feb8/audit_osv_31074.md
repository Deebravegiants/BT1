# [H] iio: pressure: zpa2326: fix information leak in triggered buffer

## Summary
Severity: High
Advisory: CVE-2024-57912
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57912
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: pressure: zpa2326: fix information leak in triggered buffer

The 'sample' local struct is used to push data to user space from a
triggered buffer, but it has a hole between the temperature and the
timestamp (u32 pressure, u16 temperature, GAP, u64 timestamp).
This hole is never initialized.

Initialize the struct to zero before using it to avoid pushing
uninitialized information to userspace.

## References
- https://git.kernel.org/stable/c/6007d10c5262f6f71479627c1216899ea7f09073
- https://git.kernel.org/stable/c/64a989aa7475b8e76e69b9ec86819ea293e53bab
- https://git.kernel.org/stable/c/9629ff1a86823269b12fb1ba9ca4efa945906287
- https://git.kernel.org/stable/c/979a0db76ceda8fe1f2f85a116bfe97620ebbadf
- https://git.kernel.org/stable/c/b7849f62e61242e0e02c776e1109eb81e59c567c
- https://git.kernel.org/stable/c/d25f1fc273670271412a52a1efbdaf5dcf274ed8
- https://git.kernel.org/stable/c/fefb88a4da961a0b9c2473cbdcfce1a942fcfa9a
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57912.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57912
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
