# [H] CVE-2022-47940

## Summary
Severity: High
Advisory: CVE-2022-47940
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47940
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.18 before 5.18.18. fs/ksmbd/smb2pdu.c lacks length validation in the non-padding case in smb2_write.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.18
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=158a66b245739e15858de42c0ba60fcf3de9b8e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47940.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47940
- https://github.com/torvalds/linux/commit/158a66b245739e15858de42c0ba60fcf3de9b8e6
