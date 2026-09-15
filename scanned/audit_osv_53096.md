# [M] CVE-2022-2873

## Summary
Severity: Medium
Advisory: CVE-2022-2873
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-2873
Type: osv

## Details
An out-of-bounds memory access flaw was found in the Linux kernel Intel’s iSMT SMBus host controller driver in the way a user triggers the I2C_SMBUS_BLOCK_DATA (with the ioctl I2C_SMBUS) with malicious input data. This flaw allows a local user to crash the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lore.kernel.org/lkml/20220729093451.551672-1-zheyuma97%40gmail.com/T/
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://security.netapp.com/advisory/ntap-20230120-0001/
- https://www.debian.org/security/2023/dsa-5324
