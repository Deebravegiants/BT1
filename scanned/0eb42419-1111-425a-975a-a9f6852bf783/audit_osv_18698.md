# [M] CVE-2020-35506

## Summary
Severity: Medium
Advisory: CVE-2020-35506
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2020-35506
Type: osv

## Details
A use-after-free vulnerability was found in the am53c974 SCSI host bus adapter emulation of QEMU in versions before 6.0.0 during the handling of the 'Information Transfer' command (CMD_TI). This flaw allows a privileged guest user to crash the QEMU process on the host, resulting in a denial of service or potential code execution with the privileges of the QEMU process.

## References
- http://www.openwall.com/lists/oss-security/2021/04/16/3
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210713-0006/
- https://www.openwall.com/lists/oss-security/2021/04/16/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1909996
