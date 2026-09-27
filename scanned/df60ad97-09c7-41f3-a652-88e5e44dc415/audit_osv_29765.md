# [H] usb: dwc3: st: fix probed platform device ref count on probe error path

## Summary
Severity: High
Advisory: CVE-2024-46674
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46674
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.321, >=4.20.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.108, >=6.2.0 <6.6.49, >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: st: fix probed platform device ref count on probe error path

The probe function never performs any paltform device allocation, thus
error path "undo_platform_dev_alloc" is entirely bogus.  It drops the
reference count from the platform device being probed.  If error path is
triggered, this will lead to unbalanced device reference counts and
premature release of device resources, thus possible use-after-free when
releasing remaining devm-managed resources.

## References
- https://git.kernel.org/stable/c/060f41243ad7f6f5249fa7290dda0c01f723d12d
- https://git.kernel.org/stable/c/1de989668708ce5875efc9d669d227212aeb9a90
- https://git.kernel.org/stable/c/4c6735299540f3c82a5033d35be76a5c42e0fb18
- https://git.kernel.org/stable/c/6aee4c5635d81f4809c3b9f0c198a65adfbb2ada
- https://git.kernel.org/stable/c/b0979a885b9d4df2a25b88e9d444ccaa5f9f495c
- https://git.kernel.org/stable/c/ddfcfeba891064b88bb844208b43bef2ef970f0c
- https://git.kernel.org/stable/c/e1e5e8ea2731150d5ba7c707f9e02fafebcfeb49
- https://git.kernel.org/stable/c/f3498650df0805c75b4e1c94d07423c46cbf4ce1
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46674.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
