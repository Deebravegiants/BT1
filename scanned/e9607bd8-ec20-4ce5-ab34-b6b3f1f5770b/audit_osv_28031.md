# [M] spi: spi-mt65xx: Fix NULL pointer access in interrupt handler

## Summary
Severity: Medium
Advisory: CVE-2024-27028
Ecosystem: Linux
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27028
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-mt65xx: Fix NULL pointer access in interrupt handler

The TX buffer in spi_transfer can be a NULL pointer, so the interrupt
handler may end up writing to the invalid memory and cause crashes.

Add a check to trans->tx_buf before using it.

## References
- https://git.kernel.org/stable/c/1784053cf10a14c4ebd8a890bad5cfe1bee51713
- https://git.kernel.org/stable/c/2342b05ec5342a519e00524a507f7a6ea6791a38
- https://git.kernel.org/stable/c/55f8ea6731aa64871ee6aef7dba53ee9f9f3b2f6
- https://git.kernel.org/stable/c/62b1f837b15cf3ec2835724bdf8577e47d14c753
- https://git.kernel.org/stable/c/766ec94cc57492eab97cbbf1595bd516ab0cb0e4
- https://git.kernel.org/stable/c/a20ad45008a7c82f1184dc6dee280096009ece55
- https://git.kernel.org/stable/c/bcfcdf19698024565eff427706ebbd8df65abd11
- https://git.kernel.org/stable/c/bea82355df9e1c299625405b1947fc9b26b4c6d4
- https://git.kernel.org/stable/c/c10fed329c1c104f375a75ed97ea3abef0786d62
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27028.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
