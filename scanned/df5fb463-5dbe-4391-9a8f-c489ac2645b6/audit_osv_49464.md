# [H] CVE-2019-12818

## Summary
Severity: High
Advisory: CVE-2019-12818
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-14
Source: https://osv.dev/vulnerability/CVE-2019-12818
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.20.15. The nfc_llcp_build_tlv function in net/nfc/llcp_commands.c may return NULL. If the caller does not check for this, it will trigger a NULL pointer dereference. This will cause denial of service. This affects nfc_llcp_build_gb in net/nfc/llcp_core.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00040.html
- http://packetstormsecurity.com/files/154245/Kernel-Live-Patch-Security-Notice-LSN-0054-1.html
- https://support.f5.com/csp/article/K91444306
- https://security.netapp.com/advisory/ntap-20190710-0002/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.15
- http://www.securityfocus.com/bid/108776
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=58bdd544e2933a21a51eecf17c3f5f94038261b5
- https://github.com/torvalds/linux/commit/58bdd544e2933a21a51eecf17c3f5f94038261b5
