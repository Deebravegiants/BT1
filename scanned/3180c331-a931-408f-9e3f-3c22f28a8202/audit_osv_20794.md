# [H] CVE-2021-3713

## Summary
Severity: High
Advisory: CVE-2021-3713
CVSS: 7.4 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-08-25
Source: https://osv.dev/vulnerability/CVE-2021-3713
Type: osv

## Details
An out-of-bounds write flaw was found in the UAS (USB Attached SCSI) device emulation of QEMU in versions prior to 6.2.0-rc0. The device uses the guest supplied stream number unchecked, which can lead to out-of-bounds access to the UASDevice->data3 and UASDevice->status3 fields. A malicious guest user could use this flaw to crash QEMU or potentially achieve code execution with the privileges of the QEMU process on the host.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210923-0006/
- https://www.debian.org/security/2021/dsa-4980
- https://bugzilla.redhat.com/show_bug.cgi?id=1994640
