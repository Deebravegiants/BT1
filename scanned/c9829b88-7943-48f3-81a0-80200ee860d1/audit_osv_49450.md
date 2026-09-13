# [M] CVE-2019-12380

## Summary
Severity: Medium
Advisory: CVE-2019-12380
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-12380
Type: osv

## Details
**DISPUTED** An issue was discovered in the efi subsystem in the Linux kernel through 5.1.5. phys_efi_set_virtual_address_map in arch/x86/platform/efi/efi.c and efi_call_phys_prolog in arch/x86/platform/efi/efi_64.c mishandle memory allocation failures. NOTE: This id is disputed as not being an issue because “All the code touched by the referenced commit runs only at boot, before any user processes are started. Therefore, there is no possibility for an unprivileged user to control it.”.

## References
- https://usn.ubuntu.com/4414-1/
- https://usn.ubuntu.com/4439-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KLGWJKLMTBBB53D5QLS4HOY2EH246WBE/
- https://usn.ubuntu.com/4427-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J36BIJTKEPUOZKJNHQBUZA47RQONUKOI/
- https://security.netapp.com/advisory/ntap-20190710-0002/
- http://www.securityfocus.com/bid/108477
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=4e78921ba4dd0aca1cc89168f45039add4183f8e
