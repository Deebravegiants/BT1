# [H] CVE-2022-47942

## Summary
Severity: High
Advisory: CVE-2022-47942
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47942
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.19 before 5.19.2. There is a heap-based buffer overflow in set_ntacl_dacl, related to use of SMB2_QUERY_INFO_HE after a malformed SMB2_SET_INFO_HE command.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8f0541186e9ad1b62accc9519cc2b7a7240272a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47942.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47942
- https://www.zerodayinitiative.com/advisories/ZDI-22-1688/
- https://github.com/torvalds/linux/commit/8f0541186e9ad1b62accc9519cc2b7a7240272a7
