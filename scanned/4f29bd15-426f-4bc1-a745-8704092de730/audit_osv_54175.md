# [M] CVE-2023-4132

## Summary
Severity: Medium
Advisory: CVE-2023-4132
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-03
Source: https://osv.dev/vulnerability/CVE-2023-4132
Type: osv

## Details
A use-after-free vulnerability was found in the siano smsusb module in the Linux kernel. The bug occurs during device initialization when the siano device is plugged in. This flaw allows a local user to crash the system, causing a denial of service condition.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://access.redhat.com/errata/RHSA-2023:7077
- https://access.redhat.com/errata/RHSA-2024:0575
- https://access.redhat.com/errata/RHSA-2024:0724
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:6901
- https://access.redhat.com/security/cve/CVE-2023-4132
- https://security.netapp.com/advisory/ntap-20231020-0005/
- https://www.debian.org/security/2023/dsa-5480
- https://bugzilla.redhat.com/show_bug.cgi?id=2221707
