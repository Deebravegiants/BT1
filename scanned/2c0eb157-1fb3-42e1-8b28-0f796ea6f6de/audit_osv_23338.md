# [H] CVE-2022-47943

## Summary
Severity: High
Advisory: CVE-2022-47943
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47943
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel 5.15 through 5.19 before 5.19.2. There is an out-of-bounds read and OOPS for SMB2_WRITE, when there is a large length in the zero DataOffset case.

## References
- http://www.openwall.com/lists/oss-security/2022/12/23/10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ac60778b87e45576d7bfdbd6f53df902654e6f09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47943.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47943
- https://security.netapp.com/advisory/ntap-20230216-0006/
- https://www.zerodayinitiative.com/advisories/ZDI-22-1691/
- https://github.com/torvalds/linux/commit/ac60778b87e45576d7bfdbd6f53df902654e6f09
