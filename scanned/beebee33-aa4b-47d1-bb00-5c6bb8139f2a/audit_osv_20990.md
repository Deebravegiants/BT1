# [M] CVE-2021-3930

## Summary
Severity: Medium
Advisory: CVE-2021-3930
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-3930
Type: osv

## Details
An off-by-one error was found in the SCSI device emulation in QEMU. It could occur while processing MODE SELECT commands in mode_sense_page() if the 'page' argument was set to MODE_PAGE_ALLS (0x3f). A malicious guest could use this flaw to potentially crash QEMU, resulting in a denial of service condition.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00002.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220225-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=2020588
