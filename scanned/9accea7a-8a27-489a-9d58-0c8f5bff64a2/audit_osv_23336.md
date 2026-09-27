# [H] CVE-2022-47941

## Summary
Severity: High
Advisory: CVE-2022-47941
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47941
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.19 before 5.19.2. fs/ksmbd/smb2pdu.c omits a kfree call in certain smb2_handle_negotiate error conditions, aka a memory leak.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=aa7253c2393f6dcd6a1468b0792f6da76edad917
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47941.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47941
- https://www.zerodayinitiative.com/advisories/ZDI-22-1687/
- https://github.com/torvalds/linux/commit/aa7253c2393f6dcd6a1468b0792f6da76edad917
