# [H] CVE-2023-5972

## Summary
Severity: High
Advisory: CVE-2023-5972
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-23
Source: https://osv.dev/vulnerability/CVE-2023-5972
Type: osv

## Details
A null pointer dereference flaw was found in the nft_inner.c functionality of netfilter in the Linux kernel. This issue could allow a local user to crash the system or escalate their privileges on the system.

## References
- https://access.redhat.com/security/cve/CVE-2023-5972
- https://bugzilla.redhat.com/show_bug.cgi?id=2248189
- https://github.com/torvalds/linux/commit/505ce0630ad5d31185695f8a29dde8d29f28faa7
- https://github.com/torvalds/linux/commit/52177bbf19e6e9398375a148d2e13ed492b40b80
