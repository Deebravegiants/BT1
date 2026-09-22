# [M] CVE-2020-12769

## Summary
Severity: Medium
Advisory: CVE-2020-12769
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12769
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.4.17. drivers/spi/spi-dw.c allows attackers to cause a panic via concurrent calls to dw_spi_irq and dw_spi_transfer_one, aka CID-19b61392c5a8.

## References
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4391-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.17
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=19b61392c5a852b4e8a0bf35aecb969983c5932d
- https://lkml.org/lkml/2020/2/3/559
