# [H] spi: mpc52xx: Add cancel_work_sync before module remove

## Summary
Severity: High
Advisory: CVE-2024-50051
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-50051
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: mpc52xx: Add cancel_work_sync before module remove

If we remove the module which will call mpc52xx_spi_remove
it will free 'ms' through spi_unregister_controller.
while the work ms->work will be used. The sequence of operations
that may lead to a UAF bug.

Fix it by ensuring that the work is canceled before proceeding with
the cleanup in mpc52xx_spi_remove.

## References
- https://git.kernel.org/stable/c/373d55a47dc662e5e30d12ad5d334312f757c1f1
- https://git.kernel.org/stable/c/90b72189de2cddacb26250579da0510b29a8b82b
- https://git.kernel.org/stable/c/984836621aad98802d92c4a3047114cf518074c8
- https://git.kernel.org/stable/c/cd5106c77d6d6828aa82449f01f4eb436d602a21
- https://git.kernel.org/stable/c/d0cde3911cf24e1bcdd4caa1d1b9ef57589db5a1
- https://git.kernel.org/stable/c/e0c6ce8424095c2da32a063d3fc027494c689817
- https://git.kernel.org/stable/c/f65d85bc1ffd8a2c194bb2cd65e35ed3648ddd59
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50051.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
