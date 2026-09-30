# [M] CVE-2023-6039

## Summary
Severity: Medium
Advisory: CVE-2023-6039
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-09
Source: https://osv.dev/vulnerability/CVE-2023-6039
Type: osv

## Details
A use-after-free flaw was found in lan78xx_disconnect in drivers/net/usb/lan78xx.c in the network sub-component, net/usb/lan78xx in the Linux Kernel. This flaw allows a local attacker to crash the system when the LAN78XX USB device detaches.

## References
- https://access.redhat.com/security/cve/CVE-2023-6039
- https://bugzilla.redhat.com/show_bug.cgi?id=2248755
- https://github.com/torvalds/linux/commit/1e7417c188d0a83fb385ba2dbe35fd2563f2b6f3
