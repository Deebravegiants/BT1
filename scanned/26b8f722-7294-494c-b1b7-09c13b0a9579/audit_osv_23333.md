# [M] CVE-2022-47938

## Summary
Severity: Medium
Advisory: CVE-2022-47938
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47938
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.19 before 5.19.2. fs/ksmbd/smb2misc.c has an out-of-bounds read and OOPS for SMB2_TREE_CONNECT.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=824d4f64c20093275f72fc8101394d75ff6a249e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47938.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47938
- https://www.zerodayinitiative.com/advisories/ZDI-22-1689/
- https://github.com/torvalds/linux/commit/824d4f64c20093275f72fc8101394d75ff6a249e
