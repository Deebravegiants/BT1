# [M] CVE-2019-20908

## Summary
Severity: Medium
Advisory: CVE-2019-20908
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2019-20908
Type: osv

## Details
An issue was discovered in drivers/firmware/efi/efi.c in the Linux kernel before 5.4. Incorrect access permissions for the efivar_ssdt ACPI variable could be used by attackers to bypass lockdown or secure boot restrictions, aka CID-1957a85b0032.

## References
- http://www.openwall.com/lists/oss-security/2020/07/30/3
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4
- https://mailarchives.bentasker.co.uk/Mirrors/OSSSec/2020/06-Jun/msg00035.html
- https://usn.ubuntu.com/4427-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- http://www.openwall.com/lists/oss-security/2020/07/20/6
- https://usn.ubuntu.com/4426-1/
- https://usn.ubuntu.com/4439-1/
- https://usn.ubuntu.com/4440-1/
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- http://www.openwall.com/lists/oss-security/2020/07/30/2
- https://git.zx2c4.com/american-unsigned-language/tree/american-unsigned-language.sh
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1957a85b0032a81e6482ca4aab883643b8dae06e
