# [M] CVE-2020-13253

## Summary
Severity: Medium
Advisory: CVE-2020-13253
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-27
Source: https://osv.dev/vulnerability/CVE-2020-13253
Type: osv

## Details
sd_wp_addr in hw/sd/sd.c in QEMU 4.2.0 uses an unvalidated address, which leads to an out-of-bounds read during sdhci_write() operations. A guest OS user can crash the QEMU process.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00013.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202011-09
- https://usn.ubuntu.com/4467-1/
- http://www.openwall.com/lists/oss-security/2020/05/27/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1838546
- https://lists.gnu.org/archive/html/qemu-devel/2020-05/msg05835.html
