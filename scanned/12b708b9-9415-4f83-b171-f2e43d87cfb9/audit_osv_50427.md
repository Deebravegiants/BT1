# [M] CVE-2020-15780

## Summary
Severity: Medium
Advisory: CVE-2020-15780
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2020-15780
Type: osv

## Details
An issue was discovered in drivers/acpi/acpi_configfs.c in the Linux kernel before 5.7.7. Injection of malicious ACPI tables via configfs could be used by attackers to bypass lockdown and secure boot restrictions, aka CID-75b0cea7bf30.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.7
- https://usn.ubuntu.com/4425-1/
- https://usn.ubuntu.com/4439-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00047.html
- http://www.openwall.com/lists/oss-security/2020/07/30/2
- http://www.openwall.com/lists/oss-security/2020/07/30/3
- https://usn.ubuntu.com/4426-1/
- https://usn.ubuntu.com/4440-1/
- https://www.openwall.com/lists/oss-security/2020/06/15/3
- http://www.openwall.com/lists/oss-security/2020/07/20/7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=75b0cea7bf307f362057cc778efe89af4c615354
- https://git.zx2c4.com/american-unsigned-language/tree/american-unsigned-language-2.sh
