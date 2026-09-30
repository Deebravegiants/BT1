# [H] iscsi_ibft: Fix UBSAN shift-out-of-bounds warning in ibft_attr_show_nic()

## Summary
Severity: High
Advisory: CVE-2025-21993
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21993
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iscsi_ibft: Fix UBSAN shift-out-of-bounds warning in ibft_attr_show_nic()

When performing an iSCSI boot using IPv6, iscsistart still reads the
/sys/firmware/ibft/ethernetX/subnet-mask entry. Since the IPv6 prefix
length is 64, this causes the shift exponent to become negative,
triggering a UBSAN warning. As the concept of a subnet mask does not
apply to IPv6, the value is set to ~0 to suppress the warning message.

## References
- https://git.kernel.org/stable/c/07e0d99a2f701123ad3104c0f1a1e66bce74d6e5
- https://git.kernel.org/stable/c/2d1eef248107bdf3d5a69d0fde04c30a79a7bf5d
- https://git.kernel.org/stable/c/9bfa80c8aa4e06dff55a953c3fffbfc68a3a3b1c
- https://git.kernel.org/stable/c/a858cd58dea06cf85b142673deea8c5d87f11e70
- https://git.kernel.org/stable/c/b253660fac5e0e9080d2c95e3a029e1898d49afb
- https://git.kernel.org/stable/c/b388e185bfad32bfed6a97a6817f74ca00a4318f
- https://git.kernel.org/stable/c/c1c6e527470e5eab0b2d57bd073530fbace39eab
- https://git.kernel.org/stable/c/f763c82db8166e28f45b7cc4a5398a7859665940
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21993.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21993
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
