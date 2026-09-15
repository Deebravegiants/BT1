# [M] CVE-2019-12984

## Summary
Severity: Medium
Advisory: CVE-2019-12984
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12984
Type: osv

## Details
A NULL pointer dereference vulnerability in the function nfc_genl_deactivate_target() in net/nfc/netlink.c in the Linux kernel before 5.1.13 can be triggered by a malicious user-mode program that omits certain NFC attributes, leading to denial of service.

## References
- http://packetstormsecurity.com/files/154245/Kernel-Live-Patch-Security-Notice-LSN-0054-1.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4093-1/
- https://usn.ubuntu.com/4117-1/
- https://usn.ubuntu.com/4118-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.13
- https://security.netapp.com/advisory/ntap-20190806-0001/
- https://www.debian.org/security/2019/dsa-4495
- http://www.securityfocus.com/bid/108905
- https://github.com/torvalds/linux/commit/385097a3675749cbc9e97c085c0e5dfe4269ca51
