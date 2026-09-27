# [M] CVE-2023-3108

## Summary
Severity: Medium
Advisory: CVE-2023-3108
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-11
Source: https://osv.dev/vulnerability/CVE-2023-3108
Type: osv

## Details
A flaw was found in the subsequent get_user_pages_fast in the Linux kernel’s interface for symmetric key cipher algorithms in the skcipher_recvmsg of crypto/algif_skcipher.c function. This flaw allows a local user to crash the system.

## References
- https://access.redhat.com/security/cve/CVE-2023-3108
- https://bugzilla.redhat.com/show_bug.cgi?id=2221472
- https://github.com/torvalds/linux/commit/9399f0c51489ae8c16d6559b82a452fdc1895e91
