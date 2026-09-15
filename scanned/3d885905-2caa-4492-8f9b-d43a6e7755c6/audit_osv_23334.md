# [C] CVE-2022-47939

## Summary
Severity: Critical
Advisory: CVE-2022-47939
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47939
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.19 before 5.19.2. fs/ksmbd/smb2pdu.c has a use-after-free and OOPS for SMB2_TREE_DISCONNECT.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cf6531d98190fa2cf92a6d8bbc8af0a4740a223c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47939.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47939
- https://www.zerodayinitiative.com/advisories/ZDI-22-1690/
- https://github.com/torvalds/linux/commit/cf6531d98190fa2cf92a6d8bbc8af0a4740a223c
- https://www.secpod.com/blog/zero-day-server-message-block-smb-server-in-linux-kernel-5-15-has-a-critical-vulnerability-patch-ksmbd-immediately/
