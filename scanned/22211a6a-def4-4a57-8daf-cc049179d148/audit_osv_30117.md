# [M] ublk: don't allow user copy for unprivileged device

## Summary
Severity: Medium
Advisory: CVE-2024-50080
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50080
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: don't allow user copy for unprivileged device

UBLK_F_USER_COPY requires userspace to call write() on ublk char
device for filling request buffer, and unprivileged device can't
be trusted.

So don't allow user copy for unprivileged device.

## References
- https://git.kernel.org/stable/c/42aafd8b48adac1c3b20fe5892b1b91b80c1a1e6
- https://git.kernel.org/stable/c/6414ab5c9c9c068eca6dc4fd3a036bc4b83164dc
- https://git.kernel.org/stable/c/8f3d5686a2409877c5e8e2540774d24ed2b4a4ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50080.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
