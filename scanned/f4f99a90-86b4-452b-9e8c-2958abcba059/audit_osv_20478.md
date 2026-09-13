# [M] CVE-2021-3409

## Summary
Severity: Medium
Advisory: CVE-2021-3409
CVSS: 5.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2021-3409
Type: osv

## Details
The patch for CVE-2020-17380/CVE-2020-25085 was found to be ineffective, thus making QEMU vulnerable to the out-of-bounds read/write access issues previously found in the SDHCI controller emulation code. This flaw allows a malicious privileged guest to crash the QEMU process on the host, resulting in a denial of service or potential code execution. QEMU up to (including) 5.2.0 is affected by this.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00009.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210507-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1928146
- https://www.openwall.com/lists/oss-security/2021/03/09/1
